from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from authem.models import User
from Account.models import Account


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    account = models.ForeignKey(Account, related_name='transactions', on_delete=models.CASCADE)
    destination_account = models.ForeignKey(Account, null=True, blank=True, related_name='incoming_transfers', on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_cancelled = models.BooleanField(default=False)
    cancel_reason = models.TextField(blank=True, null=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='cancelled_transactions')

    def clean(self):
        try:
            if self.transaction_type == 'transfer':
                if not self.destination_account:
                    raise ValidationError("Le compte de destination est requis pour un transfert.")
                if self.account.balance < self.amount:
                    raise ValidationError("Solde insuffisant sur le compte source pour effectuer le transfert.")
            elif self.transaction_type == 'withdrawal':
                if self.account.balance < self.amount:
                    raise ValidationError("Solde insuffisant pour effectuer le retrait.")
        except ValidationError as e:
            TransactionErrorLog.objects.create(
                user=self.user,
                transaction_type=self.transaction_type,
                account=self.account,
                destination_account=self.destination_account,
                amount=self.amount,
                error_message=str(e)
            )
            raise e

    def apply(self):
        if self.transaction_type == 'deposit':
            self.account.balance += self.amount
        elif self.transaction_type == 'withdrawal':
            self.account.balance -= self.amount
        elif self.transaction_type == 'transfer':
            self.account.balance -= self.amount
            if self.destination_account:
                self.destination_account.balance += self.amount
        self.account.save()
        if self.destination_account:
            self.destination_account.save()

    def cancel(self, reason="", cancelled_by=None):
        if self.is_cancelled:
            return
        if self.transaction_type == 'deposit':
            self.account.balance -= self.amount
        elif self.transaction_type == 'withdrawal':
            self.account.balance += self.amount
        elif self.transaction_type == 'transfer':
            self.account.balance += self.amount
            if self.destination_account:
                self.destination_account.balance -= self.amount
        self.account.save()
        if self.destination_account:
            self.destination_account.save()
        self.is_cancelled = True
        self.cancel_reason = reason
        self.cancelled_at = timezone.now()
        self.cancelled_by = cancelled_by
        self.save()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if not self.is_cancelled:
            self.apply()

    def __str__(self):
        if self.transaction_type == 'transfer':
            return f"Transfer of {self.amount} from {self.account.name} to {self.destination_account.name}"
        return f"{self.transaction_type.capitalize()} of {self.amount} on {self.account.name}"


class TransactionErrorLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(max_length=20)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='error_logs')
    destination_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_error_logs')
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.transaction_type} error by {self.user}"

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

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
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_cancelled = models.BooleanField(default=False)
    cancel_reason = models.TextField(blank=True, null=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='cancelled_transactions')

    def clean(self):
        # Vérifie l'existence du compte source
        if not Account.objects.filter(pk=self.account_id).exists():
            raise ValidationError("Le compte source spécifié n'existe pas.")

        # Vérifie le type de transaction
        if self.transaction_type == 'transfer':
            if not self.destination_account:
                raise ValidationError("Le compte de destination est requis pour un transfert.")
            if not Account.objects.filter(pk=self.destination_account_id).exists():
                raise ValidationError("Le compte de destination spécifié n'existe pas.")
            # vérifier que le compte source peut couvrir montant + coût
            if (self.account.balance or Decimal('0')) < (self.amount + (self.cost or Decimal('0'))):
                raise ValidationError("Solde insuffisant sur le compte source pour effectuer le transfert (montant + coût).")

        elif self.transaction_type == 'withdrawal':
            # vérifier que le compte source peut couvrir montant + coût
            if (self.account.balance or Decimal('0')) < (self.amount + (self.cost or Decimal('0'))):
                raise ValidationError("Solde insuffisant pour effectuer le retrait (montant + coût).")

    def apply(self):
        # Applique la transaction en tenant compte du coût
        if self.transaction_type == 'deposit':
            # dépôt net après frais
            net = self.amount - (self.cost or Decimal('0'))
            self.account.balance += net
        elif self.transaction_type == 'withdrawal':
            # retrait + frais
            total = self.amount + (self.cost or Decimal('0'))
            self.account.balance -= total
        elif self.transaction_type == 'transfer':
            total = self.amount + (self.cost or Decimal('0'))
            self.account.balance -= total
            if self.destination_account:
                self.destination_account.balance += self.amount
        self.account.save()
        if self.destination_account:
            self.destination_account.save()

    def cancel(self, reason="", cancelled_by=None):
        if self.is_cancelled:
            return
        # Annule l'effet de la transaction (y compris le coût)
        if self.transaction_type == 'deposit':
            net = self.amount - (self.cost or Decimal('0'))
            self.account.balance -= net
        elif self.transaction_type == 'withdrawal':
            total = self.amount + (self.cost or Decimal('0'))
            self.account.balance += total
        elif self.transaction_type == 'transfer':
            total = self.amount + (self.cost or Decimal('0'))
            self.account.balance += total
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
        try:
            self.full_clean()
        except ValidationError as e:
            TransactionErrorLog.objects.create(
                user=self.user,
                transaction_type=self.transaction_type,
                account=self.account if Account.objects.filter(pk=self.account_id).exists() else None,
                destination_account=self.destination_account if self.destination_account and Account.objects.filter(pk=self.destination_account_id).exists() else None,
                amount=self.amount,
                error_message=str(e)
            )
            raise
        super().save(*args, **kwargs)
        if not self.is_cancelled:
            self.apply()

    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     super().save(*args, **kwargs)
    #     if not self.is_cancelled:
    #         self.apply()

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

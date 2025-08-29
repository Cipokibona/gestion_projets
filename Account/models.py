from django.db import models
from authem.models import User
from EnterpriseWallet.models import EnterpriseWallet


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('bank', 'Bank'),
    ]

    OWNER_TYPES = [
        ('user', 'User'),
        ('enterprise', 'Enterprise'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    wallet = models.ForeignKey(EnterpriseWallet, related_name='accounts', on_delete=models.CASCADE)
    owner_type = models.CharField(max_length=20, choices=OWNER_TYPES)
    owner_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='owned_accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        owner = self.owner_user.username if self.owner_type == 'user' and self.owner_user else "Enterprise"
        return f"{self.name} ({self.account_type}) - Owned by {owner}"

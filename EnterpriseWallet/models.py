from django.db import models
from authem.models import User


class EnterpriseWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enterprise_wallets')
    name = models.CharField(max_length=100, default="Main Wallet Entreprise")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def total_balance(self):
        return sum(account.balance for account in self.accounts.all())

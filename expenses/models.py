from django.db import models
from authem.models import User
from projects.models import Project
from Account.models import Account
from finance.models import TaskWallet


class MaterialExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='material_expenses')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='material_expenses')
    task_wallet = models.ForeignKey(TaskWallet, on_delete=models.SET_NULL, null=True, blank=True, related_name='material_expenses')
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)


class MiscExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='misc_expenses')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='misc_expenses')
    task_wallet = models.ForeignKey(TaskWallet, on_delete=models.SET_NULL, null=True, blank=True, related_name='misc_expenses')
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)


class GeneralExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='general_expenses')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='general_expenses')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='general_expenses')
    date = models.DateField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def amount(self):
        return sum(item.total_price for item in self.items.all())


class ExpenseItem(models.Model):
    expense = models.ForeignKey(GeneralExpense, on_delete=models.CASCADE, related_name='items')
    product_service_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Expense Item"
        verbose_name_plural = "Expense Items"


class CompanyExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_expenses')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='company_expenses')
    date = models.DateField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

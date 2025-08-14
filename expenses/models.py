from django.db import models
from projects.models import Project
from finance.models import TaskWallet


class MaterialExpense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='material_expenses')
    task_wallet = models.ForeignKey(TaskWallet, on_delete=models.SET_NULL, null=True, blank=True, related_name='material_expenses')
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)


class MiscExpense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='misc_expenses')
    task_wallet = models.ForeignKey(TaskWallet, on_delete=models.SET_NULL, null=True, blank=True, related_name='misc_expenses')
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)

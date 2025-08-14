from django.db import models
from projects.models import Project
from authem.models import User


class Advance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advances')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='advances')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class MainWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='main_wallets')
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='main_wallet')

    @property
    def current_amount(self):
        total_advances = sum(a.amount for a in self.project.advances.all())
        material_expenses = sum(e.quantity * e.unit_price for e in self.project.material_expenses.all())
        misc_expenses = sum(d.amount for d in self.project.misc_expenses.all())
        workforce_expenses = sum(w.total_cost for w in self.project.workforce_groups.all())
        taskwallets_initial = sum(t.initial_amount for t in self.task_wallets.all())
        # Ajoute le reste des TaskWallets clôturés
        taskwallets_returned = sum(t.remaining_amount for t in self.task_wallets.filter(is_closed=True))
        return total_advances - (material_expenses + misc_expenses + workforce_expenses + taskwallets_initial) + taskwallets_returned


class TaskWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_wallets')
    main_wallet = models.ForeignKey(MainWallet, on_delete=models.CASCADE, related_name='task_wallets')
    task_name = models.CharField(max_length=255)
    initial_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)

    @property
    def amount_used(self):
        material_expenses = sum(e.quantity * e.unit_price for e in self.material_expenses.all())
        misc_expenses = sum(d.amount for d in self.misc_expenses.all())
        workforce_expenses = sum(w.total_cost for w in self.workforce_groups.all())
        return material_expenses + misc_expenses + workforce_expenses

    @property
    def remaining_amount(self):
        return self.initial_amount - self.amount_used

    def close(self):
        if not self.is_closed:
            self.is_closed = True
            self.save()

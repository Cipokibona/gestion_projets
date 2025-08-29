from django.db import models
from authem.models import User
from projects.models import Project


class WorkforceGroup(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('jour', 'Journalier'),
        ('mois', 'Mensuel'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workforce_groups')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='workforce_groups')
    task_name = models.CharField(max_length=255)
    number_of_workers = models.IntegerField()
    wage = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    payment_type = models.CharField(max_length=5, choices=PAYMENT_TYPE_CHOICES, default='jour')

    @property
    def total_cost(self):
        if self.payment_type == 'jour':
            return self.number_of_workers * self.wage * self.duration_days
        elif self.payment_type == 'mois':
            months = self.duration_days / 30
            return self.number_of_workers * self.wage * months
        return 0

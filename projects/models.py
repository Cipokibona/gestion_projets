from django.db import models
from authem.models import User


class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In_progress'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('suspended', 'Suspended'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    extra_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_status(self, continue_if_exceeded=False, extra_amount=0):
        from finance.models import Advance

        has_advance = Advance.objects.filter(project=self).exists()

        if not has_advance and self.status == 'in_progress':
            raise ValueError("Impossible de passer le projet en 'in_progress' sans au moins une avance enregistrée.")

        if has_advance and self.status == 'pending':
            self.status = 'in_progress'
            self.save()

        # total_advances = Advance.objects.filter(project=self).aggregate(models.Sum('amount'))['amount__sum'] or 0

        # if total_advances > 0 and self.status == 'pending':
        #     self.status = 'in_progress'

        # if total_advances >= self.estimated_budget:
        #     if total_advances == self.estimated_budget:
        #         # Ici, tu dois demander à l'utilisateur si le projet continue
        #         if continue_if_exceeded:
        #             self.status = 'in_progress'
        #             self.extra_amount = extra_amount
        #         else:
        #             self.status = 'successful'
        #     else:  # total_advances > estimated_budget
        #         if continue_if_exceeded:
        #             self.status = 'in_progress'
        #             self.extra_amount = total_advances - self.estimated_budget
        #         else:
        #             self.status = 'successful'
        # self.save()

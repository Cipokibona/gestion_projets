from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    """
    ROLE_CHOICES = [
        ('manager', 'Project Manager'),
        ('accountant', 'Accountant'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

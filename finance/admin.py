from django.contrib import admin
from .models import Advance, MainWallet, TaskWallet

# Register your models here.
admin.site.register(Advance)
admin.site.register(MainWallet)
admin.site.register(TaskWallet)

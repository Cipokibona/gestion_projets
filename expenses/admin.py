from django.contrib import admin
from .models import MaterialExpense, MiscExpense, GeneralExpense, CompanyExpense

# Register your models here.
admin.site.register(MaterialExpense)
admin.site.register(MiscExpense)
admin.site.register(GeneralExpense)
admin.site.register(CompanyExpense)
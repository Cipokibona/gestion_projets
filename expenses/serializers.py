from rest_framework import serializers
from .models import MaterialExpense, MiscExpense


class MaterialExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialExpense
        fields = '__all__'


class MiscExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiscExpense
        fields = '__all__'

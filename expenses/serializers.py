from rest_framework import serializers
from .models import MaterialExpense, MiscExpense, GeneralExpense


class MaterialExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialExpense
        fields = '__all__'


class MiscExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiscExpense
        fields = '__all__'


class GeneralExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralExpense
        fields = '__all__'

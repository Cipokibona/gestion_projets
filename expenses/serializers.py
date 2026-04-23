from rest_framework import serializers
from .models import MaterialExpense, MiscExpense, GeneralExpense, CompanyExpense, ExpenseItem


class ExpenseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseItem
        fields = ['id', 'product_service_name', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['total_price']


class MaterialExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialExpense
        fields = '__all__'


class MiscExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiscExpense
        fields = '__all__'


class GeneralExpenseSerializer(serializers.ModelSerializer):
    items = ExpenseItemSerializer(many=True, required=False)
    amount = serializers.ReadOnlyField()

    class Meta:
        model = GeneralExpense
        fields = ['id', 'user', 'project', 'name', 'description', 'account', 'date', 'is_valid', 'created_at', 'items', 'amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        expense = GeneralExpense.objects.create(**validated_data)
        for item_data in items_data:
            ExpenseItem.objects.create(expense=expense, **item_data)
        return expense

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        instance = super().update(instance, validated_data)
        
        # Delete existing items and create new ones
        instance.items.all().delete()
        for item_data in items_data:
            ExpenseItem.objects.create(expense=instance, **item_data)
        return instance


class CompanyExpenseSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    compte_name = serializers.CharField(source='account.name', read_only=True)
    class Meta:
        model = CompanyExpense
        fields = '__all__'

class CompanyExpenseSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    compte_name = serializers.CharField(source='account.name', read_only=True)
    class Meta:
        model = CompanyExpense
        fields = '__all__'

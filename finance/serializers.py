from rest_framework import serializers
from .models import Advance, MainWallet, TaskWallet


class AdvanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advance
        fields = '__all__'


class MainWalletSerializer(serializers.ModelSerializer):
    current_amount = serializers.SerializerMethodField()

    class Meta:
        model = MainWallet
        fields = ['id', 'user', 'project', 'current_amount']

    def get_current_amount(self, obj):
        return obj.current_amount


class TaskWalletSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.SerializerMethodField()

    class Meta:
        model = TaskWallet
        fields = '__all__'

    def get_remaining_amount(self, obj):
        return obj.remaining_amount

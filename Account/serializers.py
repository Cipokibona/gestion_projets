from .models import Account
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'wallet', 'owner_type', 'owner_user', 'name', 'account_type', 'balance', 'created_at']

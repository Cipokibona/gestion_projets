from rest_framework import serializers
from .models import EnterpriseWallet


class EnterpriseWalletSerializer(serializers.ModelSerializer):
    total_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = EnterpriseWallet
        fields = ['id', 'name', 'created_at', 'total_balance']

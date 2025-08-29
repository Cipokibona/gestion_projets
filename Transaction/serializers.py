from rest_framework import serializers
from .models import Transaction, TransactionErrorLog


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'transaction_type', 'account',
            'destination_account', 'amount', 'description',
            'created_at', 'is_cancelled', 'cancel_reason',
            'cancelled_at', 'cancelled_by'
        ]
        read_only_fields = ['user', 'created_at', 'is_cancelled', 'cancelled_at', 'cancelled_by']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionErrorLog
        fields = [
            'id', 'timestamp', 'user', 'transaction_type',
            'account', 'destination_account', 'amount',
            'error_message'
        ]

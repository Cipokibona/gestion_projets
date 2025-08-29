from django.contrib import admin
from .models import Transaction, TransactionErrorLog


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'transaction_type', 'amount', 'account',
        'destination_account', 'user', 'is_cancelled',
        'cancelled_at', 'cancelled_by'
    )
    list_filter = ('transaction_type', 'is_cancelled', 'user', 'account')
    search_fields = ('description', 'user__username', 'account__name', 'destination_account__name')
    ordering = ('-created_at',)


@admin.register(TransactionErrorLog)
class TransactionErrorLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'user', 'transaction_type', 'account',
        'destination_account', 'amount', 'short_error'
    )
    list_filter = ('transaction_type', 'timestamp', 'user', 'account', 'destination_account')
    search_fields = ('error_message', 'user__username', 'account__name', 'destination_account__name')
    ordering = ('-timestamp',)

    def short_error(self, obj):
        return (obj.error_message[:75] + '...') if len(obj.error_message) > 75 else obj.error_message
    short_error.short_description = "Erreur"

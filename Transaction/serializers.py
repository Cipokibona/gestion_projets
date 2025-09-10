from rest_framework import serializers
from .models import Transaction, TransactionErrorLog
from Account.models import Account


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    destination_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'transaction_type', 'account',
            'destination_account', 'amount', 'description',
            'created_at', 'is_cancelled', 'cancel_reason',
            'cancelled_at', 'cancelled_by'
        ]
        read_only_fields = ['user', 'created_at', 'is_cancelled', 'cancelled_at', 'cancelled_by']

    def validate(self, data):
        account = data.get('account')
        destination_account = data.get('destination_account')
        amount = data.get('amount')
        transaction_type = data.get('transaction_type')

        # Vérifie que le compte source existe
        if not Account.objects.filter(pk=account.pk).exists():
            raise serializers.ValidationError({"account": "Le compte source spécifié n'existe pas."})

        if transaction_type == 'transfer':
            if not destination_account:
                raise serializers.ValidationError({"destination_account": "Le compte de destination est requis pour un transfert."})
            if not Account.objects.filter(pk=destination_account.pk).exists():
                raise serializers.ValidationError({"destination_account": "Le compte de destination spécifié n'existe pas."})
            if account == destination_account:
                raise serializers.ValidationError({"destination_account": "Le compte source et le compte de destination doivent être différents."})
            if account.balance < amount:
                raise serializers.ValidationError({"amount": "Solde insuffisant sur le compte source pour effectuer le transfert."})

        elif transaction_type == 'withdrawal':
            if account.balance < amount:
                raise serializers.ValidationError({"amount": "Solde insuffisant pour effectuer le retrait."})

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        transaction = super().create(validated_data)
        # Applique le mouvement de solde
        if not transaction.is_cancelled:
            if transaction.transaction_type == 'deposit':
                transaction.account.balance += transaction.amount
            elif transaction.transaction_type == 'withdrawal':
                transaction.account.balance -= transaction.amount
            elif transaction.transaction_type == 'transfer':
                transaction.account.balance -= transaction.amount
                if transaction.destination_account:
                    transaction.destination_account.balance += transaction.amount
            transaction.account.save()
            if transaction.destination_account:
                transaction.destination_account.save()
        return transaction


# class TransactionSerializer(serializers.ModelSerializer):
#     account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
#     destination_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)

#     class Meta:
#         model = Transaction
#         fields = [
#             'id', 'user', 'transaction_type', 'account',
#             'destination_account', 'amount', 'description',
#             'created_at', 'is_cancelled', 'cancel_reason',
#             'cancelled_at', 'cancelled_by'
#         ]
#         read_only_fields = ['user', 'created_at', 'is_cancelled', 'cancelled_at', 'cancelled_by']

#         def validate(self, data):
#             account = data.get('account')
#             destination_account = data.get('destination_account')
#             amount = data.get('amount')
#             transaction_type = data.get('transaction_type')

#             # Vérifie que le compte source existe
#             if not Account.objects.filter(pk=account.pk).exists():
#                 raise serializers.ValidationError({"account": "Le compte source spécifié n'existe pas."})

#             if transaction_type == 'transfer':
#                 if not destination_account:
#                     raise serializers.ValidationError({"destination_account": "Le compte de destination est requis pour un transfert."})
#                 if not Account.objects.filter(pk=destination_account.pk).exists():
#                     raise serializers.ValidationError({"destination_account": "Le compte de destination spécifié n'existe pas."})
#                 if account == destination_account:
#                     raise serializers.ValidationError({"destination_account": "Le compte source et le compte de destination doivent être différents."})
#                 if account.balance < amount:
#                     raise serializers.ValidationError({"amount": "Solde insuffisant sur le compte source pour effectuer le transfert."})

#             elif transaction_type == 'withdrawal':
#                 if account.balance < amount:
#                     raise serializers.ValidationError({"amount": "Solde insuffisant pour effectuer le retrait."})

#             return data

#         # def validate(self, data):
#         #     account = data.get('account')
#         #     destination_account = data.get('destination_account')
#         #     amount = data.get('amount')
#         #     transaction_type = data.get('transaction_type')

#         #     if not account:
#         #         raise serializers.ValidationError({"account": "Le compte source est requis."})

#         #     if transaction_type == 'transfer':
#         #         if not destination_account:
#         #             raise serializers.ValidationError({"destination_account": "Le compte de destination est requis pour un transfert."})
#         #         if account == destination_account:
#         #             raise serializers.ValidationError({"destination_account": "Le compte source et le compte de destination doivent être différents."})
#         #         if account.balance < amount:
#         #             raise serializers.ValidationError({"amount": "Solde insuffisant sur le compte source pour effectuer le transfert."})

#         #     elif transaction_type == 'withdrawal':
#         #         if account.balance < amount:
#         #             raise serializers.ValidationError({"amount": "Solde insuffisant pour effectuer le retrait."})

#         #     return data

#         def create(self, validated_data):
#             user = self.context['request'].user
#             validated_data['user'] = user
#             return super().create(validated_data)

#     # def validate_account(self, account):
#     #     if not Account.objects.filter(pk=account.pk).exists():
#     #         raise serializers.ValidationError("Le compte source spécifié n'existe pas.")
#     #     return account

#     # def validate_destination_account(self, destination_account):
#     #     if destination_account and not Account.objects.filter(pk=destination_account.pk).exists():
#     #         raise serializers.ValidationError("Le compte de destination spécifié n'existe pas.")
#     #     return destination_account

#     # def validate(self, data):
#     #     account = data.get('account')
#     #     destination_account = data.get('destination_account')
#     #     amount = data.get('amount')
#     #     transaction_type = data.get('transaction_type')

#     #     if transaction_type == 'transfer':
#     #         if not destination_account:
#     #             raise serializers.ValidationError({"destination_account": "Le compte de destination est requis pour un transfert."})
#     #         if account.balance < amount:
#     #             raise serializers.ValidationError({"amount": "Solde insuffisant sur le compte source pour effectuer le transfert."})

#     #     elif transaction_type == 'withdrawal':
#     #         if account.balance < amount:
#     #             raise serializers.ValidationError({"amount": "Solde insuffisant pour effectuer le retrait."})

#     #     return data

#     # def create(self, validated_data):
#     #     user = self.context['request'].user
#     #     validated_data['user'] = user

#     #     transaction = Transaction.objects.create(**validated_data)

#     #     if not transaction.is_cancelled:
#     #         if transaction.transaction_type == 'deposit':
#     #             transaction.account.balance += transaction.amount
#     #         elif transaction.transaction_type == 'withdrawal':
#     #             transaction.account.balance -= transaction.amount
#     #         elif transaction.transaction_type == 'transfer':
#     #             transaction.account.balance -= transaction.amount
#     #             transaction.destination_account.balance += transaction.amount

#     #         transaction.account.save()
#     #         if transaction.destination_account:
#     #             transaction.destination_account.save()

#     #     return transaction


# # class TransactionSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Transaction
# #         fields = [
# #             'id', 'user', 'transaction_type', 'account',
# #             'destination_account', 'amount', 'description',
# #             'created_at', 'is_cancelled', 'cancel_reason',
# #             'cancelled_at', 'cancelled_by'
# #         ]
# #         read_only_fields = ['user', 'created_at', 'is_cancelled', 'cancelled_at', 'cancelled_by']

# #     def validate(self, data):
# #         account = data.get('account')
# #         destination_account = data.get('destination_account')
# #         amount = data.get('amount')
# #         transaction_type = data.get('transaction_type')
# #         user = self.context['request'].user

# #         try:
# #             if not Account.objects.filter(pk=account.pk).exists():
# #                 raise serializers.ValidationError("Le compte source spécifié n'existe pas.")

# #             if transaction_type == 'transfer':
# #                 if not destination_account:
# #                     raise serializers.ValidationError("Le compte de destination est requis pour un transfert.")
# #                 if not Account.objects.filter(pk=destination_account.pk).exists():
# #                     raise serializers.ValidationError("Le compte de destination spécifié n'existe pas.")
# #                 if account.balance < amount:
# #                     raise serializers.ValidationError("Solde insuffisant sur le compte source pour effectuer le transfert.")

# #             elif transaction_type == 'withdrawal':
# #                 if account.balance < amount:
# #                     raise serializers.ValidationError("Solde insuffisant pour effectuer le retrait.")

# #         except serializers.ValidationError as e:
# #             TransactionErrorLog.objects.create(
# #                 user=user,
# #                 transaction_type=transaction_type,
# #                 account=account if Account.objects.filter(pk=account.pk).exists() else None,
# #                 destination_account=destination_account if destination_account and Account.objects.filter(pk=destination_account.pk).exists() else None,
# #                 amount=amount,
# #                 error_message=str(e)
# #             )
# #             raise e

# #         return data

# #     def create(self, validated_data):
# #         user = self.context['request'].user
# #         validated_data['user'] = user

# #         transaction = Transaction.objects.create(**validated_data)

# #         # Appliquer la transaction ici (sans dépendre du modèle)
# #         if not transaction.is_cancelled:
# #             if transaction.transaction_type == 'deposit':
# #                 transaction.account.balance += transaction.amount
# #             elif transaction.transaction_type == 'withdrawal':
# #                 transaction.account.balance -= transaction.amount
# #             elif transaction.transaction_type == 'transfer':
# #                 transaction.account.balance -= transaction.amount
# #                 if transaction.destination_account:
# #                     transaction.destination_account.balance += transaction.amount

# #             transaction.account.save()
# #             if transaction.destination_account:
# #                 transaction.destination_account.save()

# #         return transaction

# #     # def create(self, validated_data):
# #     #     validated_data['user'] = self.context['request'].user
# #     #     return super().create(validated_data)

# #     # def validate_account(self, account):
# #     #     if not Account.objects.filter(id=account.id).exists():
# #     #         raise serializers.ValidationError("Le compte spécifié n'existe pas.")
# #     #     return account

# #     # def validate_destination_account(self, destination_account):
# #     #     if destination_account and not Account.objects.filter(id=destination_account.id).exists():
# #     #         raise serializers.ValidationError("Le compte de destination spécifié n'existe pas.")
# #     #     return destination_account


class TransactionErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionErrorLog
        fields = [
            'id', 'timestamp', 'user', 'transaction_type',
            'account', 'destination_account', 'amount',
            'error_message'
        ]

from rest_framework import serializers
from decimal import Decimal

from .models import Transaction, TransactionErrorLog
from Account.models import Account


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    destination_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    destination_account_name = serializers.CharField(source='destination_account.name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'transaction_type', 'account',
            'destination_account', 'amount', 'cost', 'description',
            'created_at', 'is_cancelled', 'cancel_reason',
            'cancelled_at', 'cancelled_by', 'user_username','account_name', 'destination_account_name'
        ]
        read_only_fields = ['user', 'created_at', 'is_cancelled', 'cancelled_at', 'cancelled_by']

    def validate_amount(self, value):
        if value is None or value <= Decimal('0'):
            raise serializers.ValidationError("Le montant doit être strictement positif.")
        return value

    def validate_cost(self, value):
        if value is None:
            return Decimal('0')
        if value < Decimal('0'):
            raise serializers.ValidationError("Le coût doit être positif ou nul.")
        return value

    def validate(self, data):
        """
        Validation métier : existence des comptes, cohérence montant/coût et
        vérification que le compte source couvre montant + coût pour les sorties.
        En cas d'erreur métier, on enregistre un TransactionErrorLog puis on lève ValidationError.
        """
        account = data.get('account')
        destination_account = data.get('destination_account')
        amount = data.get('amount')
        cost = data.get('cost') or Decimal('0')
        transaction_type = data.get('transaction_type')

        try:
            # vérifications basiques
            if not account or not Account.objects.filter(pk=account.pk).exists():
                raise serializers.ValidationError({"account": "Le compte source spécifié n'existe pas."})

            if amount is None:
                raise serializers.ValidationError({"amount": "Le montant est requis."})

            if cost is None:
                cost = Decimal('0')

            if transaction_type == 'transfer':
                if not destination_account:
                    raise serializers.ValidationError({"destination_account": "Le compte de destination est requis pour un transfert."})
                if not Account.objects.filter(pk=destination_account.pk).exists():
                    raise serializers.ValidationError({"destination_account": "Le compte de destination spécifié n'existe pas."})
                if account == destination_account:
                    raise serializers.ValidationError({"destination_account": "Le compte source et le compte de destination doivent être différents."})
                total_needed = amount + cost
                if (account.balance or Decimal('0')) < total_needed:
                    raise serializers.ValidationError({"amount": "Solde insuffisant sur le compte source pour effectuer le transfert (montant + coût)."})

            elif transaction_type == 'withdrawal':
                total_needed = amount + cost
                if (account.balance or Decimal('0')) < total_needed:
                    raise serializers.ValidationError({"amount": "Solde insuffisant pour effectuer le retrait (montant + coût)."})

            elif transaction_type == 'deposit':
                # pour un dépôt, le coût ne peut excéder le montant (évite dépôt net négatif)
                if cost > amount:
                    raise serializers.ValidationError({"cost": "Le coût ne peut excéder le montant du dépôt."})

        except serializers.ValidationError as e:
            # Enregistrer l'erreur métier pour audit/debug
            try:
                user = self.context.get('request').user if self.context.get('request', None) else None
            except Exception:
                user = None

            TransactionErrorLog.objects.create(
                user=user,
                transaction_type=transaction_type,
                account=account if account and Account.objects.filter(pk=getattr(account, 'pk', None)).exists() else None,
                destination_account=destination_account if destination_account and Account.objects.filter(pk=getattr(destination_account, 'pk', None)).exists() else None,
                amount=amount or Decimal('0'),
                error_message=str(e)
            )
            raise

        return data

    def create(self, validated_data):
        # Associer l'utilisateur courant et créer l'objet.
        # Ne pas appliquer manuellement les mouvements de solde ici :
        # le modèle Transaction.save() s'occupe de full_clean() et apply().
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    # class Meta:
    #     model = Transaction
    #     fields = [
    #         'id', 'user', 'transaction_type', 'account',
    #         'destination_account', 'amount', 'cost', 'description',
    #         'created_at', 'is_cancelled', 'cancel_reason',
    #         'cancelled_at', 'cancelled_by'
    #     ]
    #     read_only_fields = ['user', 'created_at', 'is_cancelled', 'cancelled_at', 'cancelled_by']

    # def validate(self, data):
    #     account = data.get('account')
    #     destination_account = data.get('destination_account')
    #     amount = data.get('amount')
    #     transaction_type = data.get('transaction_type')

    #     # Vérifie que le compte source existe
    #     if not Account.objects.filter(pk=account.pk).exists():
    #         raise serializers.ValidationError({"account": "Le compte source spécifié n'existe pas."})

    #     if transaction_type == 'transfer':
    #         if not destination_account:
    #             raise serializers.ValidationError({"destination_account": "Le compte de destination est requis pour un transfert."})
    #         if not Account.objects.filter(pk=destination_account.pk).exists():
    #             raise serializers.ValidationError({"destination_account": "Le compte de destination spécifié n'existe pas."})
    #         if account == destination_account:
    #             raise serializers.ValidationError({"destination_account": "Le compte source et le compte de destination doivent être différents."})
    #         if account.balance < amount:
    #             raise serializers.ValidationError({"amount": "Solde insuffisant sur le compte source pour effectuer le transfert."})

    #     elif transaction_type == 'withdrawal':
    #         if account.balance < amount:
    #             raise serializers.ValidationError({"amount": "Solde insuffisant pour effectuer le retrait."})

    #     return data

    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     validated_data['user'] = user
    #     transaction = super().create(validated_data)
    #     # Applique le mouvement de solde
    #     if not transaction.is_cancelled:
    #         if transaction.transaction_type == 'deposit':
    #             transaction.account.balance += transaction.amount
    #         elif transaction.transaction_type == 'withdrawal':
    #             transaction.account.balance -= transaction.amount
    #         elif transaction.transaction_type == 'transfer':
    #             transaction.account.balance -= transaction.amount
    #             if transaction.destination_account:
    #                 transaction.destination_account.balance += transaction.amount
    #         transaction.account.save()
    #         if transaction.destination_account:
    #             transaction.destination_account.save()
    #     return transaction


class TransactionErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionErrorLog
        fields = [
            'id', 'timestamp', 'user', 'transaction_type',
            'account', 'destination_account', 'amount',
            'error_message'
        ]

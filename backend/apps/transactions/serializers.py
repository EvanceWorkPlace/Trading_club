from rest_framework import serializers

from .models import Transaction, TransactionLog


class TransactionSerializer(serializers.ModelSerializer):
    #Serializer for transactions.
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display',
            'amount', 'status', 'status_display',
            'description', 'reference_number',
            'group_id', 'contribution_id',
            'created_at', 'completed_at'
        ]


class TransactionListSerializer(serializers.ModelSerializer):
    #Lightweight serializer for transaction lists.
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'amount',
            'status', 'description', 'created_at'
        ]


class TransactionFilterSerializer(serializers.Serializer):
    #Serializer for filtering transactions.
    transaction_type = serializers.ChoiceField(
        choices=Transaction.TRANSACTION_TYPES,
        required=False
    )
    status = serializers.ChoiceField(
        choices=Transaction.STATUS_CHOICES,
        required=False
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    min_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False
    )
    max_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False
    )


class TransactionSummarySerializer(serializers.Serializer):
    #Serializer for transaction summary.
    total_transactions = serializers.IntegerField()
    total_credits = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_debits = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_flow = serializers.DecimalField(max_digits=15, decimal_places=2)
    by_type = serializers.DictField()


class TransactionLogSerializer(serializers.ModelSerializer):
    #Serializer for transaction logs.
    performed_by_name = serializers.CharField(
        source='performed_by.full_name',
        read_only=True
    )
    
    class Meta:
        model = TransactionLog
        fields = [
            'id', 'action', 'old_status', 'new_status',
            'details', 'performed_by_name', 'created_at'
        ]

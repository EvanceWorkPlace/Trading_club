from rest_framework import serializers
from decimal import Decimal

from .models import Contribution, ProfitDistribution, InvestmentSimulation
from apps.groups.models import InvestmentGroup


class ContributionSerializer(serializers.ModelSerializer):
    #Serializer for contributions.
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = Contribution
        fields = [
            'id', 'group', 'group_name', 'user', 'user_name',
            'amount', 'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status']


class ContributionCreateSerializer(serializers.ModelSerializer):
    #Serializer for creating contributions.
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('5.00')
    )
    
    class Meta:
        model = Contribution
        fields = ['group', 'amount', 'notes']
    
    def validate_amount(self, value):
        #Validate contribution amount.
        if value < Decimal('5.00'):
            raise serializers.ValidationError(
                'Minimum contribution amount is $5.00'
            )
        return value
    
    def validate_group(self, value):
        #Validate group is open for contributions.
        if value.status not in ['PENDING', 'ACTIVE']:
            raise serializers.ValidationError(
                'This group is not accepting contributions'
            )
        return value
    
    def create(self, validated_data):
        #Create contribution with current user.
        user = self.context['request'].user
        group = validated_data['group']
        amount = validated_data['amount']
        
        # Check if user has sufficient balance
        if user.wallet.balance < amount:
            raise serializers.ValidationError({
                'amount': 'Insufficient wallet balance'
            })
        
        # Deduct from wallet
        if not user.wallet.contribute(amount):
            raise serializers.ValidationError({
                'amount': 'Failed to process contribution'
            })
        
        # Create contribution
        contribution = Contribution.objects.create(
            user=user,
            group=group,
            amount=amount,
            notes=validated_data.get('notes', ''),
            status='COMPLETED'
        )
        
        # Create transaction record
        from apps.transactions.models import Transaction
        Transaction.objects.create(
            user=user,
            transaction_type='CONTRIBUTION',
            amount=amount,
            status='COMPLETED',
            description=f'Contribution to {group.name}: ${amount}'
        )
        
        return contribution


class ProfitDistributionSerializer(serializers.ModelSerializer):
    #Serializer for profit distributions.
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = ProfitDistribution
        fields = [
            'id', 'user', 'user_name', 'contribution_amount',
            'contribution_percentage', 'profit_share', 
            'total_payout', 'created_at'
        ]


class InvestmentSimulationSerializer(serializers.ModelSerializer):
    #Serializer for investment simulations.
    
    class Meta:
        model = InvestmentSimulation
        fields = [
            'id', 'principal_amount', 'interest_rate',
            'duration_months', 'projected_amount',
            'total_interest', 'created_at'
        ]
        read_only_fields = ['projected_amount', 'total_interest']
    
    def create(self, validated_data):
        #Create and calculate simulation.
        user = self.context['request'].user
        simulation = InvestmentSimulation.objects.create(
            user=user,
            **validated_data
        )
        simulation.calculate_projection()
        return simulation


class InvestmentSimulationRequestSerializer(serializers.Serializer):
    #Serializer for requesting a simulation.
    principal_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('1.00')
    )
    interest_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=4,
        min_value=Decimal('0'),
        max_value=Decimal('1'),
        default=Decimal('0.0800')
    )
    duration_months = serializers.IntegerField(
        min_value=1,
        max_value=120,
        default=12
    )
    calculation_method = serializers.ChoiceField(
        choices=['simple', 'compound'],
        default='simple'
    )


class GroupROIAnalyticsSerializer(serializers.Serializer):
    #Serializer for group ROI analytics.
    group_id = serializers.UUIDField()
    group_name = serializers.CharField()
    total_contributed = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    roi_percentage = serializers.DecimalField(max_digits=7, decimal_places=2)
    member_count = serializers.IntegerField()
    duration_months = serializers.IntegerField()
    annualized_return = serializers.DecimalField(max_digits=7, decimal_places=2)

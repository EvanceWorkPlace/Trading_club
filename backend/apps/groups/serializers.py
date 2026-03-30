from rest_framework import serializers
from decimal import Decimal

from .models import InvestmentGroup, GroupMembership, GroupInvitation
from apps.accounts.serializers import UserSerializer


class GroupMembershipSerializer(serializers.ModelSerializer):
    #Serializer for group memberships
    user = UserSerializer(read_only=True)
    contribution_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = GroupMembership
        fields = [
            'id', 'user', 'role', 'is_active',
            'total_contributed', 'profit_share',
            'contribution_percentage', 'joined_at'
        ]


class InvestmentGroupListSerializer(serializers.ModelSerializer):
    #Serializer for listing groups.
    created_by = UserSerializer(read_only=True)
     
    progress_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2, 
        read_only=True
    )
    days_remaining = serializers.IntegerField(read_only=True)
    is_fully_funded = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = InvestmentGroup
        fields = [
            'id', 'name', 'description', 'created_by',
            'target_amount', 'current_amount', 'interest_rate',
            'duration_months', 'status', 'progress_percentage',
            'days_remaining', 'is_fully_funded',
            'start_date', 'end_date', 'member_count',
            'created_at'
        ]

class InvestmentGroupDetailSerializer(serializers.ModelSerializer):
    #Serializer for detailed group view.
    created_by = UserSerializer(read_only=True)
    memberships = GroupMembershipSerializer(many=True, read_only=True)
    progress_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    days_remaining = serializers.IntegerField(read_only=True)
    is_fully_funded = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = InvestmentGroup
        fields = [
            'id', 'name', 'description', 'created_by',
            'target_amount', 'current_amount', 'interest_rate',
            'duration_months', 'total_profit', 'status',
            'progress_percentage', 'days_remaining', 'is_fully_funded',
            'start_date', 'end_date', 'member_count',
            'memberships', 'created_at', 'updated_at'
        ]


class InvestmentGroupCreateSerializer(serializers.ModelSerializer):
    #Serializer for creating investment groups.
    
    class Meta:
        model = InvestmentGroup
        fields = [
            'name', 'description', 'target_amount',
            'interest_rate', 'duration_months'
        ]
    
    def validate_target_amount(self, value):
        #Validate minimum target amount.
        if value < Decimal('100.00'):
            raise serializers.ValidationError(
                'Minimum target amount is R100.00'
            )
        return value
    
    def create(self, validated_data):
        #Create group with current user as creator.
        user = self.context['request'].user
        group = InvestmentGroup.objects.create(
            created_by=user,
            **validated_data
        )
        
        # Create admin membership for creator
        GroupMembership.objects.create(
            group=group,
            user=user,
            role='ADMIN',
            is_active=True
        )
        
        group.member_count = 1
        group.save()
        
        return group


class GroupInvitationSerializer(serializers.ModelSerializer):
    #Serializer for group invitations.
    invited_by = UserSerializer(read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = GroupInvitation
        fields = [
            'id', 'group', 'group_name', 'invited_by',
            'email', 'status', 'expires_at', 'created_at'
        ]
        read_only_fields = ['status', 'expires_at', 'invited_by']


class JoinGroupSerializer(serializers.Serializer):
    #Serializer for joining a group.
    invitation_token = serializers.CharField(required=False, allow_blank=True)


class UpdateGroupSerializer(serializers.ModelSerializer):
    #Serializer for updating group details.
    
    class Meta:
        model = InvestmentGroup
        fields = ['name', 'description']

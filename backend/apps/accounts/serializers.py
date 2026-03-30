"""
Serializers for accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

from .models import Wallet

User = get_user_model()


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet model."""
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'balance', 'total_deposited', 
            'total_contributed', 'total_earned',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    wallet = WalletSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'full_name', 'phone_number', 'avatar',
            'is_email_verified', 'date_joined', 'wallet'
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'is_email_verified']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 
            'phone_number', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """Validate passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Passwords do not match.'}
            )
        return attrs
    
    def create(self, validated_data):
        """Create new user."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'avatar']


class DepositSerializer(serializers.Serializer):
    """Serializer for depositing funds."""
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('10.00'))]
    )
    
    def validate_amount(self, value):
        """Validate minimum deposit amount."""
        if value < Decimal('10.00'):
            raise serializers.ValidationError(
                'Minimum deposit amount is $10.00'
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Passwords do not match.'}
            )
        return attrs


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google OAuth authentication."""
    access_token = serializers.CharField(required=True)

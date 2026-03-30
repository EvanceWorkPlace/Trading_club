"""
User and Wallet models for InvestClub.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with email as primary identifier."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    # OAuth fields
    google_id = models.CharField(max_length=255, blank=True, db_index=True)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def wallet_balance(self):
        """Get user's wallet balance."""
        if hasattr(self, 'wallet'):
            return self.wallet.balance
        return 0.00


class Wallet(models.Model):
    """User wallet for managing virtual funds."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )
    total_deposited = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00
    )
    total_contributed = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00
    )
    total_earned = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
    
    def __str__(self):
        return f"{self.user.email} - ${self.balance}"
    
    def deposit(self, amount):
        """Add funds to wallet."""
        from decimal import Decimal
        amount = Decimal(str(amount))
        self.balance += amount
        self.total_deposited += amount
        self.save()
        return True
    
    def withdraw(self, amount):
        """Remove funds from wallet."""
        from decimal import Decimal
        amount = Decimal(str(amount))
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False
    
    def contribute(self, amount):
        """Deduct contribution from wallet."""
        from decimal import Decimal
        amount = Decimal(str(amount))
        if self.balance >= amount:
            self.balance -= amount
            self.total_contributed += amount
            self.save()
            return True
        return False
    
    def add_earnings(self, amount):
        """Add profit share to wallet."""
        from decimal import Decimal
        amount = Decimal(str(amount))
        self.balance += amount
        self.total_earned += amount
        self.save()
        return True

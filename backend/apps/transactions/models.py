import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Transaction(models.Model):
    #Transaction model for tracking all financial activities.
    
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('CONTRIBUTION', 'Contribution'),
        ('PROFIT', 'Profit Share'),
        ('REFUND', 'Refund'),
        ('TRANSFER', 'Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    description = models.TextField(blank=True)
    
    # Related objects (optional)
    group_id = models.UUIDField(null=True, blank=True)
    contribution_id = models.UUIDField(null=True, blank=True)
    
    # Metadata
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True
    )
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        #Generate reference number if not set.
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)
    
    def generate_reference_number(self):
        #Generate unique reference number
        import random
        import string
        prefix = 'INV'
        timestamp = self.created_at.strftime('%Y%m%d') if self.created_at else '00000000'
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{timestamp}-{random_suffix}"
    
    def complete(self):
        #Mark transaction as completed.
        from django.utils import timezone
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()
    
    def fail(self, reason=''):
        #Mark transaction as failed
        self.status = 'FAILED'
        if reason:
            self.metadata['failure_reason'] = reason
        self.save()
    
    @property
    def is_credit(self):
        #Check if transaction is a credit
        return self.transaction_type in ['DEPOSIT', 'PROFIT', 'REFUND']
    
    @property
    def is_debit(self):
        #Check if transaction is a debit.
        return self.transaction_type in ['WITHDRAWAL', 'CONTRIBUTION']


class TransactionLog(models.Model):
    #Transaction log for audit trail.
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=50)
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    details = models.JSONField(default=dict, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaction Log'
        verbose_name_plural = 'Transaction Logs'
    
    def __str__(self):
        return f"{self.transaction.reference_number} - {self.action}"

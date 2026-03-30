import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Contribution(models.Model):
    #Contribution model for group investments.
    #Investment and Contribution models for InvestClub.

    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        'groups.InvestmentGroup',
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('5.00'))]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contribution'
        verbose_name_plural = 'Contributions'
    
    def __str__(self):
        return f"{self.user.email} - ${self.amount} to {self.group.name}"
    
    def save(self, *args, **kwargs):
        #Override save to update group totals.
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new and self.status == 'COMPLETED':
            # Update group current amount
            self.group.update_current_amount()
            # Update membership total contributed
            from apps.groups.models import GroupMembership
            membership, _ = GroupMembership.objects.get_or_create(
                group=self.group,
                user=self.user,
                defaults={'role': 'MEMBER', 'is_active': True}
            )
            membership.update_total_contributed()
    
    def complete(self):
        #Mark contribution as completed.
        if self.status == 'PENDING':
            self.status = 'COMPLETED'
            self.save()
            
            # Update group and membership
            self.group.update_current_amount()
            from apps.groups.models import GroupMembership
            membership, _ = GroupMembership.objects.get_or_create(
                group=self.group,
                user=self.user,
                defaults={'role': 'MEMBER', 'is_active': True}
            )
            membership.update_total_contributed()
            
            # Check if group should be activated
            if self.group.is_fully_funded and self.group.status == 'PENDING':
                self.group.activate()
            
            return True
        return False


class ProfitDistribution(models.Model):
    #Profit distribution record for group members.
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        'groups.InvestmentGroup',
        on_delete=models.CASCADE,
        related_name='profit_distributions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profit_distributions'
    )
    contribution_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    contribution_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    profit_share = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_payout = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Profit Distribution'
        verbose_name_plural = 'Profit Distributions'
        unique_together = ['group', 'user']
    
    def __str__(self):
        return f"{self.user.email} - ${self.profit_share} from {self.group.name}"


class InvestmentSimulation(models.Model):
    #Investment simulation model for projections.
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='simulations'
    )
    principal_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.0800')
    )
    duration_months = models.PositiveIntegerField(default=12)
    
    # Calculated fields
    projected_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_interest = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Investment Simulation'
        verbose_name_plural = 'Investment Simulations'
    
    def __str__(self):
        return f"Simulation: ${self.principal_amount} @ {self.interest_rate}% for {self.duration_months}mo"
    
    def calculate_projection(self):
        #Calculate investment projection using compound interest.
        from .services import ProfitCalculationService
        
        result = ProfitCalculationService.calculate_compound_interest(
            principal=float(self.principal_amount),
            annual_rate=float(self.interest_rate),
            months=self.duration_months
        )
        
        self.projected_amount = Decimal(str(result['total_amount']))
        self.total_interest = Decimal(str(result['total_interest']))
        self.save()
        
        return result

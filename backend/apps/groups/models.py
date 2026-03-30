import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings


class InvestmentGroup(models.Model):
    #Investment group model for collaborative investing.
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups'
    )
    
    # Group settings
    target_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('100.00'))]
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.0800'),  # 8% annual
        validators=[MinValueValidator(Decimal('0'))]
    )
    duration_months = models.PositiveIntegerField(
        default=12,
        validators=[MinValueValidator(1)]
    )
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Totals
    current_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    member_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Investment Group'
        verbose_name_plural = 'Investment Groups'
    
    def __str__(self):
        return f"{self.name} (${self.current_amount}/${self.target_amount})"
    
    @property
    def progress_percentage(self):
        #Calculate progress towards target.
        if self.target_amount > 0:
            return min(100, (self.current_amount / self.target_amount * 100))
        return 0
    
    @property
    def is_fully_funded(self):
        #Check if group has reached target.
        return self.current_amount >= self.target_amount
    
    @property
    def days_remaining(self):
        #Calculate days remaining until maturity.
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return max(0, delta.days)
        return None
    
    def update_current_amount(self):
        #Recalculate current amount from contributions.
        total = self.contributions.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        self.current_amount = total
        self.save(update_fields=['current_amount'])
    
    def update_member_count(self):
        #Recalculate member count.
        count = self.memberships.filter(is_active=True).count()
        self.member_count = count
        self.save(update_fields=['member_count'])
    
    def activate(self):
        #Activate the group and set dates.
        if self.status == 'PENDING' and self.is_fully_funded:
            self.status = 'ACTIVE'
            self.start_date = timezone.now().date()
            self.end_date = self.start_date + timezone.timedelta(
                days=30 * self.duration_months
            )
            self.save()
            return True
        return False
    
    def complete(self):
        #Mark group as completed and distribute profits
        if self.status == 'ACTIVE':
            from apps.investments.services import ProfitCalculationService
            
            # Calculate and distribute profits
            ProfitCalculationService.distribute_profits(self)
            
            self.status = 'COMPLETED'
            self.save()
            return True
        return False


class GroupMembership(models.Model):
    #Membership model linking users to groups.
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        InvestmentGroup,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='MEMBER'
    )
    is_active = models.BooleanField(default=True)
    
    # Contribution tracking
    total_contributed = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    profit_share = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['group', 'user']
        ordering = ['-joined_at']
        verbose_name = 'Group Membership'
        verbose_name_plural = 'Group Memberships'
    
    def __str__(self):
        return f"{self.user.email} - {self.group.name}"
    
    @property
    def contribution_percentage(self):
        #Calculate member's contribution percentage.
        if self.group.current_amount > 0:
            return (self.total_contributed / self.group.current_amount * 100)
        return 0
    
    def update_total_contributed(self):
        #Recalculate total contributed amount.
        from apps.investments.models import Contribution
        total = Contribution.objects.filter(
            group=self.group,
            user=self.user
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        self.total_contributed = total
        self.save(update_fields=['total_contributed'])


class GroupInvitation(models.Model):
    #Invitation model for joining groups.
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
        ('EXPIRED', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        InvestmentGroup,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    email = models.EmailField()
    token = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    expires_at = models.DateTimeField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Group Invitation'
        verbose_name_plural = 'Group Invitations'
    
    def __str__(self):
        return f"Invitation to {self.group.name} - {self.email}"
    
    @property
    def is_expired(self):
        #Check if invitation has expired.
        return timezone.now() > self.expires_at
    
    def accept(self, user):
        #Accept the invitation.
        if self.is_expired:
            self.status = 'EXPIRED'
            self.save()
            return None
        
        # Create membership
        membership, created = GroupMembership.objects.get_or_create(
            group=self.group,
            user=user,
            defaults={'role': 'MEMBER', 'is_active': True}
        )
        
        self.status = 'ACCEPTED'
        self.responded_at = timezone.now()
        self.save()
        
        # Update member count
        self.group.update_member_count()
        
        return membership
    
    def decline(self):
        #Decline the invitation.
        self.status = 'DECLINED'
        self.responded_at = timezone.now()
        self.save()

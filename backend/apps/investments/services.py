from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List
from django.db import transaction

from .models import Contribution, ProfitDistribution
#Profit calculation service for InvestClub.
# This service provides methods to calculate simple and compound interest,

class ProfitCalculationService:
    #Service for calculating investment profits and distributions.
    
    @staticmethod
    def calculate_simple_interest(
        principal: float,
        annual_rate: float,
        months: int
    ) -> Dict:
        
        # Calculate simple interest for an investment.
        
        # Args:
        #     principal: Initial investment amount
        #     annual_rate: Annual interest rate (e.g., 0.08 for 8%)
        #     months: Investment duration in months
            
        # Returns:
        #     Dictionary with total_amount, total_interest, and monthly_breakdown
        
        principal_dec = Decimal(str(principal))
        rate_dec = Decimal(str(annual_rate))
        
        # Simple interest: I = P * r * t
        time_years = Decimal(str(months)) / Decimal('12')
        total_interest = principal_dec * rate_dec * time_years
        total_amount = principal_dec + total_interest
        
        # Monthly breakdown
        monthly_interest = total_interest / Decimal(str(months)) if months > 0 else Decimal('0')
        monthly_breakdown = []
        
        running_total = principal_dec
        for month in range(1, months + 1):
            running_total += monthly_interest
            monthly_breakdown.append({
                'month': month,
                'interest_earned': float(monthly_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'running_total': float(running_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })
        
        return {
            'principal': float(principal_dec),
            'annual_rate': annual_rate,
            'months': months,
            'total_interest': float(total_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_amount': float(total_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'monthly_breakdown': monthly_breakdown
        }
    
    @staticmethod
    def calculate_compound_interest(
        principal: float,
        annual_rate: float,
        months: int,
        compounds_per_year: int = 12
    ) -> Dict:
        
        # Calculate compound interest for an investment.
        
        # Args:
        #     principal: Initial investment amount
        #     annual_rate: Annual interest rate (e.g., 0.08 for 8%)
        #     months: Investment duration in months
        #     compounds_per_year: Number of times interest compounds per year
            
        # Returns:
        #     Dictionary with total_amount, total_interest, and monthly_breakdown

        principal_dec = Decimal(str(principal))
        rate_dec = Decimal(str(annual_rate))
        
        # Compound interest: A = P * (1 + r/n)^(nt)
        n = Decimal(str(compounds_per_year))
        t = Decimal(str(months)) / Decimal('12')
        
        total_amount = principal_dec * (
            (1 + rate_dec / n) ** (n * t)
        )
        total_interest = total_amount - principal_dec
        
        # Monthly breakdown (approximation for monthly display)
        monthly_breakdown = []
        running_total = principal_dec
        monthly_rate = rate_dec / Decimal('12')
        
        for month in range(1, months + 1):
            interest = running_total * monthly_rate
            running_total += interest
            monthly_breakdown.append({
                'month': month,
                'interest_earned': float(interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'running_total': float(running_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })
        
        return {
            'principal': float(principal_dec),
            'annual_rate': annual_rate,
            'months': months,
            'compounds_per_year': compounds_per_year,
            'total_interest': float(total_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_amount': float(total_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'monthly_breakdown': monthly_breakdown
        }
    
    @staticmethod
    def calculate_profit_distribution(
        group,
        calculation_method: str = 'simple'
    ) -> List[Dict]:
        
        # Calculate profit distribution for all group members.
        
        # Args:
        #     group: InvestmentGroup instance
        #     calculation_method: 'simple' or 'compound'
            
        # Returns:
        #     List of distribution records for each member
        
        from apps.groups.models import GroupMembership
        
        total_amount = Decimal(str(group.current_amount))
        annual_rate = Decimal(str(group.interest_rate))
        months = group.duration_months
        
        # Calculate total profit
        if calculation_method == 'compound':
            result = ProfitCalculationService.calculate_compound_interest(
                float(total_amount),
                float(annual_rate),
                months
            )
        else:
            result = ProfitCalculationService.calculate_simple_interest(
                float(total_amount),
                float(annual_rate),
                months
            )
        
        total_profit = Decimal(str(result['total_interest']))
        
        # Get all active memberships
        memberships = GroupMembership.objects.filter(
            group=group,
            is_active=True
        )
        
        distributions = []
        for membership in memberships:
            contribution = Decimal(str(membership.total_contributed))
            
            # Calculate percentage
            if total_amount > 0:
                percentage = (contribution / total_amount * 100)
            else:
                percentage = Decimal('0')
            
            # Calculate profit share
            profit_share = (percentage / 100) * total_profit
            total_payout = contribution + profit_share
            
            distributions.append({
                'user': membership.user,
                'membership': membership,
                'contribution_amount': contribution,
                'contribution_percentage': percentage,
                'profit_share': profit_share,
                'total_payout': total_payout
            })
        
        return distributions
    
    @staticmethod
    @transaction.atomic
    def distribute_profits(group) -> Dict:
        
        # Calculate and distribute profits to all members.
        
        # Args:
        #     group: InvestmentGroup instance
            
        # Returns:
        #     Dictionary with distribution summary
        
        from apps.transactions.models import Transaction
        
        # Calculate distributions
        distributions = ProfitCalculationService.calculate_profit_distribution(
            group,
            calculation_method='simple'
        )
        
        total_distributed = Decimal('0')
        distribution_records = []
        
        for dist in distributions:
            # Update membership profit share
            membership = dist['membership']
            membership.profit_share = dist['profit_share']
            membership.save()
            
            # Create or update profit distribution record
            profit_dist, created = ProfitDistribution.objects.update_or_create(
                group=group,
                user=dist['user'],
                defaults={
                    'contribution_amount': dist['contribution_amount'],
                    'contribution_percentage': dist['contribution_percentage'],
                    'profit_share': dist['profit_share'],
                    'total_payout': dist['total_payout']
                }
            )
            
            # Add profit to user's wallet
            wallet = dist['user'].wallet
            wallet.add_earnings(dist['profit_share'])
            
            # Create transaction record
            Transaction.objects.create(
                user=dist['user'],
                transaction_type='PROFIT',
                amount=dist['profit_share'],
                status='COMPLETED',
                description=f'Profit share from {group.name}: ${dist["profit_share"]}'
            )
            
            total_distributed += dist['profit_share']
            distribution_records.append({
                'user': dist['user'].email,
                'contribution': float(dist['contribution_amount']),
                'percentage': float(dist['contribution_percentage']),
                'profit_share': float(dist['profit_share']),
                'total_payout': float(dist['total_payout'])
            })
        
        # Update group total profit
        group.total_profit = total_distributed
        group.save()
        
        return {
            'group_id': str(group.id),
            'group_name': group.name,
            'total_profit': float(total_distributed),
            'distributions': distribution_records
        }
    
    @staticmethod
    def get_member_roi(user) -> Dict:
        
        # Calculate Return on Investment for a user.
        
        # Args:
        #     user: User instance
            
        # Returns:
        #     Dictionary with ROI statistics
    
        wallet = user.wallet
        
        total_contributed = Decimal(str(wallet.total_contributed))
        total_earned = Decimal(str(wallet.total_earned))
        
        if total_contributed > 0:
            roi_percentage = ((total_earned - total_contributed) / total_contributed) * 100
        else:
            roi_percentage = Decimal('0')
        
        return {
            'total_contributed': float(total_contributed),
            'total_earned': float(total_earned),
            'net_profit': float(total_earned - total_contributed),
            'roi_percentage': float(roi_percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        }

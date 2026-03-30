from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum

from .models import Contribution, ProfitDistribution, InvestmentSimulation
from .serializers import (
    ContributionSerializer,
    ContributionCreateSerializer,
    ProfitDistributionSerializer,
    InvestmentSimulationSerializer,
    InvestmentSimulationRequestSerializer,
    GroupROIAnalyticsSerializer
)
from .services import ProfitCalculationService


class ContributionViewSet(viewsets.ModelViewSet):
    #ViewSet for contributions.
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        #Get contributions for current user.
        return Contribution.objects.filter(
            user=self.request.user
        ).select_related('group', 'user')
    
    def get_serializer_class(self):
        #Return appropriate serializer.
        if self.action == 'create':
            return ContributionCreateSerializer
        return ContributionSerializer
    
    def perform_create(self, serializer):
        #Create contribution with current user.
        return serializer.save()
    
    @action(detail=False, methods=['get'])
    def my_contributions(self, request):
        #Get all user's contributions.
        contributions = self.get_queryset()
        
        # Filter by group if provided
        group_id = request.query_params.get('group')
        if group_id:
            contributions = contributions.filter(group_id=group_id)
        
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def group_contributions(self, request):
        #Get contributions for a specific group.
        group_id = request.query_params.get('group')
        if not group_id:
            return Response(
                {'error': 'Group ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is member of the group
        from apps.groups.models import GroupMembership
        try:
            membership = GroupMembership.objects.get(
                group_id=group_id,
                user=request.user,
                is_active=True
            )
        except GroupMembership.DoesNotExist:
            return Response(
                {'error': 'You are not a member of this group'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        contributions = Contribution.objects.filter(
            group_id=group_id
        ).select_related('user')
        
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)


class ProfitDistributionViewSet(viewsets.ReadOnlyModelViewSet):
    #ViewSet for profit distributions.
    serializer_class = ProfitDistributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        #Get profit distributions for current user.
        return ProfitDistribution.objects.filter(
            user=self.request.user
        ).select_related('group')
    
    @action(detail=False, methods=['get'])
    def my_distributions(self, request):
        #Get all user's profit distributions.
        distributions = self.get_queryset()
        serializer = ProfitDistributionSerializer(distributions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def group_distributions(self, request):
        #Get profit distributions for a specific group.
        group_id = request.query_params.get('group')
        if not group_id:
            return Response(
                {'error': 'Group ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        distributions = ProfitDistribution.objects.filter(
            group_id=group_id
        ).select_related('user')
        
        # Check if user is member
        from apps.groups.models import GroupMembership
        if not GroupMembership.objects.filter(
            group_id=group_id,
            user=request.user,
            is_active=True
        ).exists():
            return Response(
                {'error': 'You are not a member of this group'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProfitDistributionSerializer(distributions, many=True)
        return Response(serializer.data)


class InvestmentSimulationViewSet(viewsets.ModelViewSet):
    #ViewSet for investment simulations.
    serializer_class = InvestmentSimulationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        #Get simulations for current user.
        return InvestmentSimulation.objects.filter(
            user=self.request.user
        )
    
    def perform_create(self, serializer):
        #Create simulation with current user.
        return serializer.save()
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        #Calculate investment projection without saving.
        serializer = InvestmentSimulationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        if data['calculation_method'] == 'compound':
            result = ProfitCalculationService.calculate_compound_interest(
                float(data['principal_amount']),
                float(data['interest_rate']),
                data['duration_months']
            )
        else:
            result = ProfitCalculationService.calculate_simple_interest(
                float(data['principal_amount']),
                float(data['interest_rate']),
                data['duration_months']
            )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def my_simulations(self, request):
        """Get all user's simulations."""
        simulations = self.get_queryset()
        serializer = InvestmentSimulationSerializer(simulations, many=True)
        return Response(serializer.data)


class AnalyticsViewSet(viewsets.ViewSet):
    #ViewSet for investment analytics.
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def roi(self, request):
        """Get user's ROI statistics."""
        roi_data = ProfitCalculationService.get_member_roi(request.user)
        return Response(roi_data)
    
    @action(detail=False, methods=['get'])
    def group_analytics(self, request):
        #Get analytics for all user's groups.
        from apps.groups.models import InvestmentGroup, GroupMembership
        
        memberships = GroupMembership.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('group')
        
        analytics = []
        for membership in memberships:
            group = membership.group
            
            if group.status == 'COMPLETED' and group.total_profit > 0:
                total_contributed = group.current_amount
                total_profit = group.total_profit
                roi_percentage = (total_profit / total_contributed * 100) if total_contributed > 0 else 0
                
                # Calculate annualized return
                annualized = (roi_percentage / group.duration_months * 12) if group.duration_months > 0 else 0
                
                analytics.append({
                    'group_id': group.id,
                    'group_name': group.name,
                    'total_contributed': total_contributed,
                    'total_profit': total_profit,
                    'roi_percentage': round(roi_percentage, 2),
                    'member_count': group.member_count,
                    'duration_months': group.duration_months,
                    'annualized_return': round(annualized, 2)
                })
        
        serializer = GroupROIAnalyticsSerializer(data=analytics, many=True)
        serializer.is_valid()
        
        return Response(analytics)
    
    @action(detail=False, methods=['get'])
    def portfolio_summary(self, request):
        #Get portfolio summary.
        from apps.groups.models import GroupMembership
        
        user = request.user
        wallet = user.wallet
        
        # Group statistics
        memberships = GroupMembership.objects.filter(
            user=user,
            is_active=True
        )
        
        active_groups = memberships.filter(
            group__status='ACTIVE'
        ).count()
        
        pending_groups = memberships.filter(
            group__status='PENDING'
        ).count()
        
        completed_groups = memberships.filter(
            group__status='COMPLETED'
        ).count()
        
        # Contribution statistics
        total_contributions = Contribution.objects.filter(
            user=user,
            status='COMPLETED'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # ROI calculation
        roi_data = ProfitCalculationService.get_member_roi(user)
        
        return Response({
            'wallet': {
                'balance': str(wallet.balance),
                'total_deposited': str(wallet.total_deposited),
                'total_contributed': str(wallet.total_contributed),
                'total_earned': str(wallet.total_earned)
            },
            'groups': {
                'active': active_groups,
                'pending': pending_groups,
                'completed': completed_groups,
                'total': memberships.count()
            },
            'contributions': {
                'total_amount': str(total_contributions)
            },
            'roi': roi_data
        })

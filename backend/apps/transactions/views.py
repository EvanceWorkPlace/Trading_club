from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, Count
from django.utils.dateparse import parse_date

from .models import Transaction, TransactionLog
from .serializers import (
    TransactionSerializer,
    TransactionListSerializer,
    TransactionFilterSerializer,
    TransactionSummarySerializer,
    TransactionLogSerializer
)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    #ViewSet for transactions.
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        #Get transactions for current00000 user.
        return Transaction.objects.filter(
            user=self.request.user
        )
    
    def get_serializer_class(self):
        #Return appropriate serializer.
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        #Get full transaction history with filtering.
        queryset = self.get_queryset()
        
        # Apply filters
        transaction_type = request.query_params.get('type')
        status_filter = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type.upper())
        
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        if start_date:
            parsed_start = parse_date(start_date)
            if parsed_start:
                queryset = queryset.filter(created_at__date__gte=parsed_start)
        
        if end_date:
            parsed_end = parse_date(end_date)
            if parsed_end:
                queryset = queryset.filter(created_at__date__lte=parsed_end)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        #Get transaction summary.
        user = request.user
        transactions = Transaction.objects.filter(user=user)
        
        # Calculate totals
        total_count = transactions.count()
        
        credits = transactions.filter(
            transaction_type__in=['DEPOSIT', 'PROFIT', 'REFUND']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        debits = transactions.filter(
            transaction_type__in=['WITHDRAWAL', 'CONTRIBUTION']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # By type breakdown
        by_type = transactions.values('transaction_type').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')
        
        by_type_dict = {
            item['transaction_type']: {
                'count': item['count'],
                'total': str(item['total'])
            }
            for item in by_type
        }
        
        summary = {
            'total_transactions': total_count,
            'total_credits': str(credits),
            'total_debits': str(debits),
            'net_flow': str(credits - debits),
            'by_type': by_type_dict
        }
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        #Get recent transactions.
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 100)  # Max 100
        
        transactions = self.get_queryset()[:limit]
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        #Get transactions grouped by type.
        user = request.user
        
        result = {}
        for type_code, type_name in Transaction.TRANSACTION_TYPES:
            transactions = Transaction.objects.filter(
                user=user,
                transaction_type=type_code
            )[:5]
            
            result[type_code] = {
                'name': type_name,
                'count': Transaction.objects.filter(
                    user=user,
                    transaction_type=type_code
                ).count(),
                'recent': TransactionSerializer(transactions, many=True).data
            }
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        #Get transaction logs.
        transaction = self.get_object()
        logs = TransactionLog.objects.filter(transaction=transaction)
        serializer = TransactionLogSerializer(logs, many=True)
        return Response(serializer.data)


class TransactionStatsViewSet(viewsets.ViewSet):
    #ViewSet for transaction statistics.
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def monthly_breakdown(self, request):
        #Get monthly transaction breakdown.
        from django.db.models.functions import TruncMonth
        from django.utils import timezone
        from datetime import timedelta
        
        user = request.user
        
        # Last 12 months
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        
        monthly_data = Transaction.objects.filter(
            user=user,
            created_at__gte=start_date,
            status='COMPLETED'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            deposits=Sum('amount', filter=Q(transaction_type='DEPOSIT')),
            contributions=Sum('amount', filter=Q(transaction_type='CONTRIBUTION')),
            profits=Sum('amount', filter=Q(transaction_type='PROFIT'))
        ).order_by('month')
        
        result = []
        for data in monthly_data:
            result.append({
                'month': data['month'].strftime('%Y-%m') if data['month'] else None,
                'deposits': str(data['deposits'] or 0),
                'contributions': str(data['contributions'] or 0),
                'profits': str(data['profits'] or 0)
            })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def dashboard_cards(self, request):
        #Get dashboard card statistics.
        user = request.user
        
        # Today's transactions
        from django.utils import timezone
        today = timezone.now().date()
        
        today_stats = Transaction.objects.filter(
            user=user,
            created_at__date=today
        ).aggregate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        # This month's transactions
        this_month = Transaction.objects.filter(
            user=user,
            created_at__year=today.year,
            created_at__month=today.month
        ).aggregate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        # Pending transactions
        pending_count = Transaction.objects.filter(
            user=user,
            status='PENDING'
        ).count()
        
        return Response({
            'today': {
                'count': today_stats['count'] or 0,
                'total': str(today_stats['total'] or 0)
            },
            'this_month': {
                'count': this_month['count'] or 0,
                'total': str(this_month['total'] or 0)
            },
            'pending_count': pending_count
        })

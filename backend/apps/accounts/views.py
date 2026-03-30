"""
Views for accounts app.
"""
import requests
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Wallet
from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    UserProfileUpdateSerializer, DepositSerializer,
    ChangePasswordSerializer, GoogleAuthSerializer,
    WalletSerializer
)
from apps.transactions.models import Transaction

User = get_user_model()


def get_tokens_for_user(user):
    """Generate JWT tokens for user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        tokens = get_tokens_for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UpdateProfileView(generics.UpdateAPIView):
    """Update user profile."""
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class WalletDetailView(generics.RetrieveAPIView):
    """Get wallet details."""
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.wallet


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def deposit_funds(request):
    """Deposit funds to user wallet (simulated payment)."""
    serializer = DepositSerializer(data=request.data)
    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        
        with transaction.atomic():
            # Update wallet
            wallet = request.user.wallet
            wallet.deposit(amount)
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                transaction_type='DEPOSIT',
                amount=amount,
                status='COMPLETED',
                description=f'Deposit of ${amount}'
            )
        
        return Response({
            'message': f'Successfully deposited ${amount}',
            'wallet': WalletSerializer(wallet).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password."""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        
        # Check old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Incorrect password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_auth(request):
    """Authenticate user with Google OAuth."""
    serializer = GoogleAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    access_token = serializer.validated_data['access_token']
    
    # Verify token with Google
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        response.raise_for_status()
        user_data = response.json()
    except requests.RequestException:
        return Response(
            {'error': 'Invalid Google token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    email = user_data.get('email')
    google_id = user_data.get('sub')
    first_name = user_data.get('given_name', '')
    last_name = user_data.get('family_name', '')
    
    # Get or create user
    try:
        user = User.objects.get(email=email)
        # Update Google ID if not set
        if not user.google_id:
            user.google_id = google_id
            user.save()
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            google_id=google_id,
            is_email_verified=True
        )
    
    tokens = get_tokens_for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': tokens,
        'message': 'Authenticated successfully'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get user dashboard statistics."""
    user = request.user
    wallet = user.wallet
    
    # Get user's groups
    from apps.groups.models import GroupMembership
    memberships = GroupMembership.objects.filter(user=user)
    
    active_groups = memberships.filter(
        group__status='ACTIVE'
    ).count()
    
    completed_groups = memberships.filter(
        group__status='COMPLETED'
    ).count()
    
    # Calculate total ROI
    if wallet.total_contributed > 0:
        roi = ((wallet.total_earned - wallet.total_contributed) / 
               wallet.total_contributed * 100)
    else:
        roi = 0
    
    return Response({
        'wallet_balance': str(wallet.balance),
        'total_deposited': str(wallet.total_deposited),
        'total_contributed': str(wallet.total_contributed),
        'total_earned': str(wallet.total_earned),
        'active_groups': active_groups,
        'completed_groups': completed_groups,
        'roi_percentage': round(roi, 2)
    })

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    # JWT Authentication
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration
    path('register/', views.RegisterView.as_view(), name='register'),
    path('google/', views.google_auth, name='google_auth'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='profile_update'),
    path('password/change/', views.change_password, name='change_password'),
    
    # Wallet
    path('wallet/', views.WalletDetailView.as_view(), name='wallet'),
    path('wallet/deposit/', views.deposit_funds, name='deposit'),
    
    # Dashboard
    path('dashboard/', views.dashboard_stats, name='dashboard'),
]

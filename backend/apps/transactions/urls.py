from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'', views.TransactionViewSet, basename='transactions')
router.register(r'stats', views.TransactionStatsViewSet, basename='transaction-stats')

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'contributions', views.ContributionViewSet, basename='contributions')
router.register(r'profits', views.ProfitDistributionViewSet, basename='profits')
router.register(r'simulations', views.InvestmentSimulationViewSet, basename='simulations')
router.register(r'analytics', views.AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]

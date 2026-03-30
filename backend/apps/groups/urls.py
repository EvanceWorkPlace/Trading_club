from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

#URLs for groups app.
router = DefaultRouter()
router.register(r'', views.InvestmentGroupViewSet, basename='groups')
router.register(r'invitations', views.GroupInvitationViewSet, basename='invitations')

urlpatterns = [
    path('', include(router.urls)),
]

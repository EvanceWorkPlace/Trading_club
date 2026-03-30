import uuid
from datetime import timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import InvestmentGroup, GroupMembership, GroupInvitation
from .serializers import (
    InvestmentGroupListSerializer,
    InvestmentGroupDetailSerializer,
    InvestmentGroupCreateSerializer,
    GroupMembershipSerializer,
    GroupInvitationSerializer,
    JoinGroupSerializer,
    UpdateGroupSerializer
)


class InvestmentGroupViewSet(viewsets.ModelViewSet):
    #ViewSet for investment groups
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        #Get groups where user is a member.
        user = self.request.user
        return InvestmentGroup.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        ).distinct()
    
    def get_serializer_class(self):
        #Return appropriate serializer.
        if self.action == 'create':
            return InvestmentGroupCreateSerializer
        elif self.action in ['retrieve', 'my_groups']:
            return InvestmentGroupDetailSerializer
        elif self.action == 'update':
            return UpdateGroupSerializer
        return InvestmentGroupListSerializer
    
    def perform_create(self, serializer):
        #Create group with current user.
        return serializer.save()
    
    @action(detail=False, methods=['get'])
    def my_groups(self, request):
        #Get all groups where user is a member.
        groups = self.get_queryset()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            groups = groups.filter(status=status_filter.upper())
        
        serializer = InvestmentGroupDetailSerializer(groups, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def discover(self, request):
        #Discover public groups (not a member yet).
        user = request.user
        
        # Get groups where user is not a member
        groups = InvestmentGroup.objects.exclude(
            memberships__user=user
        ).filter(status='PENDING')
        
        serializer = InvestmentGroupListSerializer(groups, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        #Join a group.
        group = self.get_object()
        user = request.user
        
        serializer = JoinGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if already a member
        if GroupMembership.objects.filter(group=group, user=user).exists():
            return Response(
                {'error': 'You are already a member of this group'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check invitation token if provided
        token = serializer.validated_data.get('invitation_token')
        if token:
            try:
                invitation = GroupInvitation.objects.get(
                    token=token,
                    group=group,
                    email=user.email,
                    status='PENDING'
                )
                if invitation.is_expired:
                    return Response(
                        {'error': 'Invitation has expired'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                membership = invitation.accept(user)
            except GroupInvitation.DoesNotExist:
                return Response(
                    {'error': 'Invalid invitation token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Direct join (for public groups)
            membership = GroupMembership.objects.create(
                group=group,
                user=user,
                role='MEMBER',
                is_active=True
            )
            group.update_member_count()
        
        return Response({
            'message': 'Successfully joined the group',
            'membership': GroupMembershipSerializer(membership).data
        })
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        #Leave a group.
        group = self.get_object()
        user = request.user
        
        try:
            membership = GroupMembership.objects.get(
                group=group,
                user=user
            )
            
            # Check if user is the creator
            if group.created_by == user:
                return Response(
                    {'error': 'Group creator cannot leave. Transfer ownership first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if group is active with contributions
            if group.status == 'ACTIVE' and membership.total_contributed > 0:
                return Response(
                    {'error': 'Cannot leave active group with contributions'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            membership.delete()
            group.update_member_count()
            group.update_current_amount()
            
            return Response({'message': 'Successfully left the group'})
            
        except GroupMembership.DoesNotExist:
            return Response(
                {'error': 'You are not a member of this group'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def invite(self, request, pk=None):
        #Invite a user to join the group.
        group = self.get_object()
        user = request.user
        
        # Check if user is admin
        try:
            membership = GroupMembership.objects.get(
                group=group,
                user=user,
                role='ADMIN'
            )
        except GroupMembership.DoesNotExist:
            return Response(
                {'error': 'Only admins can invite members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already a member
        if GroupMembership.objects.filter(
            group=group,
            user__email=email
        ).exists():
            return Response(
                {'error': 'User is already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create invitation
        invitation = GroupInvitation.objects.create(
            group=group,
            invited_by=user,
            email=email,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        return Response({
            'message': 'Invitation sent successfully',
            'invitation': GroupInvitationSerializer(invitation).data
        })
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        #Get group members.
        group = self.get_object()
        memberships = GroupMembership.objects.filter(
            group=group,
            is_active=True
        )
        serializer = GroupMembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class GroupInvitationViewSet(viewsets.ReadOnlyModelViewSet):
    #ViewSet for group invitations.
    serializer_class = GroupInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        #Get invitations for current user.
        return GroupInvitation.objects.filter(
            email=self.request.user.email
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        #Accept an invitation.
        invitation = self.get_object()
        user = request.user
        
        if invitation.email != user.email:
            return Response(
                {'error': 'This invitation is not for you'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if invitation.is_expired:
            return Response(
                {'error': 'Invitation has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = invitation.accept(user)
        
        return Response({
            'message': 'Invitation accepted',
            'membership': GroupMembershipSerializer(membership).data
        })
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        #Decline an invitation.
        invitation = self.get_object()
        user = request.user
        
        if invitation.email != user.email:
            return Response(
                {'error': 'This invitation is not for you'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        invitation.decline()
        
        return Response({'message': 'Invitation declined'})

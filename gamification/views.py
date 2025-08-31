from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Streak, Badge, Achievement
from .serializers import (
    StreakSerializer, BadgeSerializer, AchievementSerializer, UserBadgeSerializer
)

class StreakViewSet(viewsets.ModelViewSet):
    serializer_class = StreakSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Streak.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_streak(self, request, pk=None):
        streak = self.get_object()
        streak.update_streak()
        serializer = self.get_serializer(streak)
        return Response(serializer.data)

class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Badge.objects.all()
    
    @action(detail=False, methods=['get'])
    def unlocked_badges(self, request):
        achievements = Achievement.objects.filter(user=request.user)
        serializer = UserBadgeSerializer(achievements, many=True)
        return Response(serializer.data)

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Achievement.objects.filter(user=self.request.user)

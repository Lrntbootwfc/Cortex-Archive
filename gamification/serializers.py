from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Streak, Badge, Achievement

class StreakSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Streak
        fields = '__all__'
        read_only_fields = ['user', 'last_updated_at']

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'
        read_only_fields = ['date_created']

class AchievementSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Achievement
        fields = '__all__'
        read_only_fields = ['user', 'date_unlocked']

class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = Achievement
        fields = ['badge', 'date_unlocked']

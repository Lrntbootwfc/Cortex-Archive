from django.contrib import admin
from .models import Streak, Badge, Achievement

@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_activity_date']
    list_filter = ['current_streak', 'longest_streak']
    search_fields = ['user__username']
    readonly_fields = ['last_updated_at']

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'unlock_condition', 'date_created']
    list_filter = ['date_created']
    search_fields = ['name', 'description']
    readonly_fields = ['date_created']

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'achievement_type', 'date_unlocked']
    list_filter = ['achievement_type', 'date_unlocked']
    search_fields = ['user__username', 'badge__name']
    readonly_fields = ['date_unlocked']

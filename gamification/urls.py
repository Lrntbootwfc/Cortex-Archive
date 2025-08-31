from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StreakViewSet, BadgeViewSet, AchievementViewSet

router = DefaultRouter()
router.register(r'streaks', StreakViewSet, basename='streak')
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'achievements', AchievementViewSet, basename='achievement')

urlpatterns = [
    path('', include(router.urls)),
]

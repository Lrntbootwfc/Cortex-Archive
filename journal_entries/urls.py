from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, JournalEntryViewSet, MediaAssetViewSet, 
    ComicEntryViewSet, UserRegistrationView
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'journal-entries', JournalEntryViewSet, basename='journal-entry')
router.register(r'media-assets', MediaAssetViewSet, basename='media-asset')
router.register(r'comic-entries', ComicEntryViewSet, basename='comic-entry')
router.register(r'register', UserRegistrationView, basename='user-register')

urlpatterns = [
    path('', include(router.urls)),
    path('create-comic/', JournalEntryViewSet.as_view({'post': 'create'}), name='create-comic'),
]

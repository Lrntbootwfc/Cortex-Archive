from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import UserProfile, JournalEntry, MediaAsset, ComicEntry
from .serializers import (
    UserProfileSerializer, JournalEntrySerializer, MediaAssetSerializer,
    ComicEntrySerializer, JournalEntryCreateSerializer, JournalEntryUpdateSerializer,
    UserRegistrationSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JournalEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JournalEntryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return JournalEntryUpdateSerializer
        return JournalEntrySerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_lock(self, request, pk=None):
        entry = self.get_object()
        entry.is_locked = not entry.is_locked
        entry.save()
        return Response({'is_locked': entry.is_locked})
    
    @action(detail=False, methods=['get'])
    def locked_entries(self, request):
        entries = self.get_queryset().filter(is_locked=True)
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='create-comic')
    def create_comic(self, request, pk=None):
        """
        Simulates AI processing to create a comic from a journal entry.
        """
        try:
            journal_entry = self.get_object()
            
            # Retrieve character ID from the request data
            character_id = request.data.get('character_id')
            if not character_id:
                return Response({'error': 'Character ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if a comic already exists for this entry
            if hasattr(journal_entry, 'comic_entry'):
                return Response({'error': 'A comic for this journal entry already exists.'}, status=status.HTTP_409_CONFLICT)
                
            # Simulate AI processing - for now, just a placeholder image
            placeholder_image_url = f"https://placehold.co/600x400/007BFF/white?text=Comic+from+Entry+{journal_entry.id}+with+Character+{character_id}"
            
            # Create a new ComicEntry object
            comic = ComicEntry.objects.create(
                journal_entry=journal_entry,
                comic_image=placeholder_image_url  # In a real app, this would be a File object
            )

            # Return the serialized comic data
            serializer = ComicEntrySerializer(comic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MediaAssetViewSet(viewsets.ModelViewSet):
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return MediaAsset.objects.filter(journal_entry__user=self.request.user)
    
    def perform_create(self, serializer):
        journal_entry_id = self.request.data.get('journal_entry')
        try:
            journal_entry = JournalEntry.objects.get(id=journal_entry_id, user=self.request.user)
            serializer.save(journal_entry=journal_entry)
        except JournalEntry.DoesNotExist:
            return Response(
                {'error': 'Journal entry not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )

class ComicEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ComicEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return ComicEntry.objects.filter(journal_entry__user=self.request.user)
    
    def perform_create(self, serializer):
        journal_entry_id = self.request.data.get('journal_entry')
        try:
            journal_entry = JournalEntry.objects.get(id=journal_entry_id, user=self.request.user)
            serializer.save(journal_entry=journal_entry)
        except JournalEntry.DoesNotExist:
            return Response(
                {'error': 'Journal entry not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )

class UserRegistrationView(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    
    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create UserProfile for the new user
            UserProfile.objects.create(user=user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLookupView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        username = request.query_params.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                return Response([{'id': user.id, 'username': user.username}])
            except User.DoesNotExist:
                return Response([], status=status.HTTP_404_NOT_FOUND)
        return Response([], status=status.HTTP_400_BAD_REQUEST)

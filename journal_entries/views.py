#journal_entries/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from .models import UserProfile, JournalEntry, MediaAsset, ComicEntry, Character, CharacterAssignment, Folder
from .serializers import (
    UserProfileSerializer, JournalEntrySerializer, MediaAssetSerializer,
    ComicEntrySerializer, JournalEntryCreateSerializer, JournalEntryUpdateSerializer,
    UserRegistrationSerializer, CharacterSerializer, CharacterAssignmentSerializer, FolderMiniSerializer,FolderTreeSerializer
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
            if ComicEntry.objects.filter(journal_entry=journal_entry).exists():
                return Response({'error': 'A comic for this journal entry already exists.'}, status=409)

            try:
                character = Character.objects.get(id=character_id, user=request.user)
            except Character.DoesNotExist:
                return Response({'error': 'Character not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Create character assignment
            if CharacterAssignment.objects.filter(journal_entry=journal_entry, character=character).exists():
                return Response({'error': 'Character already assigned to this entry'},  status=status.HTTP_400_BAD_REQUEST)

            
            # Simulate AI processing - for now, just a placeholder image
            placeholder_image_url = f"https://placehold.co/600x400/007BFF/white?text=Comic+from+Entry+{journal_entry.id}+with+{character.name}"
            
            # Create a new ComicEntry object
            comic = ComicEntry.objects.create(
                journal_entry=journal_entry,
                comic_image=placeholder_image_url,  # In a real app, this would be a File object
                generation_prompt=f"Comic featuring {character.name} as main character"
            )

            # Return the serialized comic data
            serializer = ComicEntrySerializer(comic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        entry = self.get_object()
        folder_id = request.data.get('folder')
        folder = Folder.objects.filter(id=folder_id, user=request.user).first() if folder_id else None
        entry.folder = folder
        entry.save()
        return Response({'folder': folder.id if folder else None})

    @action(detail=True, methods=['post'])
    def rename(self, request, pk=None):
        entry = self.get_object()
        title = request.data.get('title', '').strip()
        if not title:
            return Response({'error':'title required'},  status=status.HTTP_400_BAD_REQUEST)
        entry.title = title
        entry.save()
        return Response({'title': entry.title})
    
    
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
            raise NotFound("Journal entry not found or access denied")

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
            raise NotFound("Journal entry not found or access denied")

class UserRegistrationView(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    

    def perform_create(self, serializer):
        user = serializer.save()
        UserProfile.objects.create(user=user)
        return user
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

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
    
    
class CharacterViewSet(viewsets.ModelViewSet):
    serializer_class = CharacterSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Character.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class CharacterAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = CharacterAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CharacterAssignment.objects.filter(journal_entry__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save()
        
        



class FolderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FolderMiniSerializer

    def get_queryset(self):
        return Folder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['tree', 'retrieve_tree']:
            return FolderTreeSerializer
        return FolderMiniSerializer

    @action(detail=False, methods=['get'])
    def tree(self, request):
        show_hidden = request.query_params.get('show_hidden') == '1'
        roots = self.get_queryset().filter(parent__isnull=True)
        if not show_hidden:
            roots = roots.filter(is_hidden=False)
        data = FolderTreeSerializer(roots, many=True, context={'request': request}).data
        return Response(data)

    @action(detail=True, methods=['post'])
    def rename(self, request, pk=None):
        folder = self.get_object()
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'error':'name required'}, status=status.HTTP_400_BAD_REQUEST)
        folder.name = name
        folder.save()
        return Response(JournalEntrySerializer(entry).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        folder = self.get_object()
        parent_id = request.data.get('parent')
        parent = None
        if parent_id:
            parent = Folder.objects.filter(id=parent_id, user=request.user).first()
            if parent and parent.id == folder.id:
                return Response({'error':'cannot move into itself'},  status=status.HTTP_400_BAD_REQUEST)
        folder.parent = parent
        folder.save()
        return Response(FolderMiniSerializer(folder).data)

    @action(detail=True, methods=['post'])
    def toggle_lock(self, request, pk=None):
        folder = self.get_object()
        folder.is_locked = not folder.is_locked
        folder.save()
        return Response({'is_locked': folder.is_locked})

    @action(detail=True, methods=['post'])
    def toggle_hidden(self, request, pk=None):
        folder = self.get_object()
        folder.is_hidden = not folder.is_hidden
        folder.save()
        return Response({'is_hidden': folder.is_hidden})

    # Copy/Cut/Paste: we represent clipboard on client; server gets a paste call to duplicate/move
    @action(detail=True, methods=['post'])
    def paste(self, request, pk=None):
        """
        Paste items (folders/journals) into this folder.
        Payload example:
        {
            "folders": [1, 2],
            "journals": [5, 6],
            "operation": "copy" | "move"
        }
        """
        dest = self.get_object()
        op = request.data.get('operation')
        folder_ids = request.data.get('folders', [])
        journal_ids = request.data.get('journals', [])

        # --- Handle Folders ---
        for fid in folder_ids:
            f = Folder.objects.filter(id=fid, user=request.user).first()
            if not f:
                continue

            # prevent moving/copying a folder into itself
            if f.id == dest.id:
                continue

            if op == 'move':
                f.parent = dest
                f.save()

            elif op == 'copy':
                f = Folder.objects.filter(id=fid, user=request.user) \
                    .prefetch_related('journals', 'subfolders') \
                    .first()

                def clone_folder(src, new_parent):
                    # create cloned folder
                    clone = Folder.objects.create(
                        user=request.user,
                        parent=new_parent,
                        name=f"{src.name} (Copy)",
                        color=src.color,
                        is_locked=src.is_locked,
                        is_hidden=src.is_hidden
                    )
                    # clone journals inside
                    for j in src.journals.all():
                        JournalEntry.objects.create(
                            user=request.user,
                            title=f"{j.title} (Copy)",
                            content=j.content,
                            mood_tag=j.mood_tag,
                            folder=clone,
                            is_locked=j.is_locked
                        )
                    # recursively clone subfolders
                    for sub in src.subfolders.all():
                        clone_folder(sub, clone)

                clone_folder(f, dest)

        # --- Handle Journals ---
        for jid in journal_ids:
            j = JournalEntry.objects.filter(id=jid, user=request.user).first()
            if not j:
                continue

            if op == 'move':
                j.folder = dest
                j.save()

            elif op == 'copy':
                JournalEntry.objects.create(
                    user=request.user,
                    title=f"{j.title} (Copy)",
                    content=j.content,
                    mood_tag=j.mood_tag,
                    folder=dest,
                    is_locked=j.is_locked
                )

        return Response({'status': 'ok'})

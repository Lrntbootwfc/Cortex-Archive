#journal_entries/ serializer.py


from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, JournalEntry, MediaAsset, ComicEntry, Character, CharacterAssignment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user', 'date_created', 'date_updated']

class MediaAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = '__all__'
        read_only_fields = ['date_uploaded']

class ComicEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComicEntry
        # fields = '__all__'
        fields = ['id', 'journal_entry', 'comic_image', 'generation_prompt', 'date_generated']
        read_only_fields = ['date_generated']

class JournalEntrySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    media_assets = MediaAssetSerializer(many=True, read_only=True)
    comic_entry = ComicEntrySerializer(read_only=True)
    
    class Meta:
        model = JournalEntry
        fields = '__all__'
        read_only_fields = ['user', 'date_created', 'date_updated']
        
    def get_comic_entry(self, obj):
        comic = getattr(obj, 'comic_entry', None)
        return ComicEntrySerializer(comic).data if comic else None

class JournalEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ['title', 'content', 'mood_tag', 'is_locked', 'folder']

class JournalEntryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ['title', 'content', 'mood_tag', 'is_locked', 'folder']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CharacterSerializer(serializers.ModelSerializer):
    
    user = UserSerializer(read_only=True)
    class Meta:
        # You need to import the Character model at the top of the file
        model = Character
        fields = ['id', 'user', 'name', 'description', 'relationship', 'avatar', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        
class CharacterAssignmentSerializer(serializers.ModelSerializer):
    character = CharacterSerializer(read_only=True)
    journal_entry = JournalEntrySerializer(read_only=True)

    # Allow assigning via IDs
    character_id = serializers.PrimaryKeyRelatedField(
        queryset=Character.objects.all(), write_only=True, source='character'
    )
    journal_entry_id = serializers.PrimaryKeyRelatedField(
        queryset=JournalEntry.objects.all(), write_only=True, source='journal_entry'
    )

    class Meta:
        model = CharacterAssignment
        fields = ['id', 'character', 'journal_entry', 'role', 'character_id', 'journal_entry_id']
        read_only_fields = ['id']
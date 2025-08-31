from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, JournalEntry, MediaAsset, ComicEntry

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
        fields = '__all__'
        read_only_fields = ['date_generated']

class JournalEntrySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    media_assets = MediaAssetSerializer(many=True, read_only=True)
    comic_entry = ComicEntrySerializer(read_only=True)
    
    class Meta:
        model = JournalEntry
        fields = '__all__'
        read_only_fields = ['user', 'date_created', 'date_updated']

class JournalEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ['title', 'content', 'mood_tag', 'is_locked']

class JournalEntryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ['title', 'content', 'mood_tag', 'is_locked']

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

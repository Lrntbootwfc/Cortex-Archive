from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# from .models import JournalEntry
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    experience_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#ffffff')  # Hex color
    is_locked = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'parent', 'name')  # nice for Explorer-like behavior
        ordering = ['name']
        
    def clone(self, user, parent=None):
        """
        Create a copy of this folder (without subfolders/journals).
    """
        return Folder.objects.create(
            user=user,
            parent=parent,
            name=f"{self.name}_copy",
            color=self.color,
            is_locked=self.is_locked,
            is_hidden=self.is_hidden,
    )
class JournalEntry(models.Model):
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('excited', 'Excited'),
        ('calm', 'Calm'),
        ('anxious', 'Anxious'),
        ('angry', 'Angry'),
        ('grateful', 'Grateful'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    title = models.CharField(max_length=255)
    content = models.JSONField(blank=True, null=True)  # Compatible with Lexical editor
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    mood_tag = models.CharField(max_length=50, choices=MOOD_CHOICES, blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='journals')
    is_locked = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def clone(self, user, folder=None):
        """
    Create a copy of this journal entry.
    """
        return JournalEntry.objects.create(
            user=user,
            title=f"{self.title} (Copy)",
            content=self.content,
            mood_tag=self.mood_tag,
            folder=folder,
            is_locked=self.is_locked,
    )
    
    class Meta:
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        ordering = ['-date_created']

class MediaAsset(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='media_assets')
    file = models.FileField(upload_to='media/')
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    caption = models.CharField(max_length=255, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file.name} - {self.journal_entry.title}"
    
    class Meta:
        verbose_name = "Media Asset"
        verbose_name_plural = "Media Assets"

class ComicEntry(models.Model):
    journal_entry = models.OneToOneField(JournalEntry, on_delete=models.CASCADE, related_name='comic_entry')
    comic_image = models.ImageField(upload_to='comics/')
    date_generated = models.DateTimeField(auto_now_add=True)
    generation_prompt = models.TextField(blank=True)
    
    def __str__(self):
        return f"Comic for {self.journal_entry.title}"
    
    class Meta:
        verbose_name = "Comic Entry"
        verbose_name_plural = "Comic Entries"

# models.py
class Character(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    relationship = models.CharField(max_length=100, blank=True)  # friend, family, etc.
    avatar = models.ImageField(upload_to='character_avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class CharacterAssignment(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)  # main_character, mentioned, etc.
    
    def __str__(self):
        return f"{self.character.name} in {self.journal_entry.title} as {self.role}"

from django.contrib import admin
from .models import UserProfile, JournalEntry, MediaAsset, ComicEntry

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'experience_points', 'level', 'date_created']
    list_filter = ['level', 'date_created']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['date_created', 'date_updated']

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'mood_tag', 'is_locked', 'date_created']
    list_filter = ['mood_tag', 'is_locked', 'date_created']
    search_fields = ['title', 'user__username']
    readonly_fields = ['date_created', 'date_updated']
    list_editable = ['is_locked']

@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ['file', 'journal_entry', 'file_type', 'date_uploaded']
    list_filter = ['file_type', 'date_uploaded']
    search_fields = ['caption', 'journal_entry__title']

@admin.register(ComicEntry)
class ComicEntryAdmin(admin.ModelAdmin):
    list_display = ['journal_entry', 'date_generated']
    list_filter = ['date_generated']
    search_fields = ['journal_entry__title']
    readonly_fields = ['date_generated']

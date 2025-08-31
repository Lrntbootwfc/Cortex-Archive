from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Streak: {self.current_streak} days"
    
    def update_streak(self):
        today = timezone.now().date()
        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days
            if days_diff == 1:
                self.current_streak += 1
            elif days_diff > 1:
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_activity_date = today
        self.save()
    
    class Meta:
        verbose_name = "Streak"
        verbose_name_plural = "Streaks"

class Badge(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/')
    unlocked_by = models.ManyToManyField(User, related_name='unlocked_badges', blank=True)
    unlock_condition = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ['name']

class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('streak', 'Streak'),
        ('entries', 'Journal Entries'),
        ('comics', 'Comics Created'),
        ('media', 'Media Uploaded'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_unlocked = models.DateTimeField(auto_now_add=True)
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
    
    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
        unique_together = ['user', 'badge']
        ordering = ['-date_unlocked']

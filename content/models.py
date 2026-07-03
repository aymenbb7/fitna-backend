from django.db import models
from modules.models import Module

class Session(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    session_link = models.URLField()
    session_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date']

    def __str__(self):
        return self.title

class Document(models.Model):
    DOC_TYPES = (
        ('PDF', 'PDF'),
        ('REVIEW', 'Review'),
        ('EXERCISE', 'Exercise'),
        ('OTHER', 'Other'),
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_url = models.URLField()
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

class Video(models.Model):
    VIDEO_TYPES = (
        ('SESSION_RECORDING', 'Session Recording'),
        ('REVIEW', 'Review'),
        ('EXERCISE', 'Exercise'),
        ('OTHER', 'Other'),
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField()
    video_type = models.CharField(max_length=30, choices=VIDEO_TYPES)
    thumbnail_url = models.URLField(blank=True, null=True)
    duration_seconds = models.IntegerField(default=0)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

class VoiceMessage(models.Model):
    VOICE_TYPES = (
        ('LESSON', 'Lesson'),
        ('REVIEW', 'Review'),
        ('ANNOUNCEMENT', 'Announcement'),
        ('OTHER', 'Other'),
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='voice_messages')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    audio_url = models.URLField()
    voice_type = models.CharField(max_length=20, choices=VOICE_TYPES)
    duration_seconds = models.IntegerField(default=0)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

class Photo(models.Model):
    PHOTO_TYPES = (
        ('EXERCISE', 'Exercise'),
        ('REVIEW', 'Review'),
        ('EVENT', 'Event'),
        ('OTHER', 'Other'),
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=255, blank=True)
    photo_url = models.URLField()
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPES)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title or f"Photo {self.id}"

from django.db import models
from django.conf import settings
from modules.models import Module


class Section(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return self.title


class LessonProgress(models.Model):
    STATUS_CHOICES = (
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'},
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='student_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = [('student', 'lesson')]

    def __str__(self):
        return f"{self.student.email} - {self.lesson.title}"


class Document(models.Model):
    DOC_TYPES = (
        ('PDF', 'PDF'),
        ('REVIEW', 'Review'),
        ('EXERCISE', 'Exercise'),
        ('OTHER', 'Other'),
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_url = models.URLField(blank=True, null=True)
    document_file = models.FileField(upload_to='documents/', blank=True, null=True)
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
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='videos', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    telegram_link = models.URLField(blank=True, null=True, help_text='رابط فيديو تيليغرام')
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
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='voice_messages', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    audio_url = models.URLField(blank=True, null=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
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
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='photos', blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    photo_url = models.URLField(blank=True, null=True)
    image_file = models.FileField(upload_to='photos/', blank=True, null=True)
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPES)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title or f"Photo {self.id}"


class Session(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='sessions', blank=True, null=True)
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

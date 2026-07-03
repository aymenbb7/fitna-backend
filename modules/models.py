from django.db import models
from django.conf import settings

class Module(models.Model):
    THEME_CHOICES = (
        ('QURAN', 'Quran'),
        ('MEMORY', 'Memory'),
        ('SOROBAN', 'Soroban'),
        ('PROBLEM_SOLVING', 'Problem Solving'),
        ('HEALTH', 'Health'),
        ('HISTORY', 'History'),
        ('LANGUAGES', 'Languages'),
        ('TALENTS', 'Talents'),
        ('PSYCHOLOGY', 'Psychology'),
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default="📚")
    background_theme = models.CharField(max_length=50, choices=THEME_CHOICES)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    admin = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'MODULE_ADMIN'},
        related_name='managed_module'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    cover_image_url = models.URLField(blank=True, null=True)
    color_primary = models.CharField(max_length=7, blank=True, null=True) # hex color

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name

class ModuleSettings(models.Model):
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='settings')
    show_sessions = models.BooleanField(default=True)
    show_pdfs = models.BooleanField(default=True)
    show_videos = models.BooleanField(default=True)
    show_voice = models.BooleanField(default=True)
    show_photos = models.BooleanField(default=True)
    show_quizzes = models.BooleanField(default=True)
    show_schedule = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.module.name}"

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'},
        related_name='enrollments'
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='enrollments')
    is_primary = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    enrolled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='enrollments_created'
    )

    class Meta:
        unique_together = ['student', 'module']

    def __str__(self):
        return f"{self.student.email} in {self.module.name}"

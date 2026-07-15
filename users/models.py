from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, full_name='', role='STUDENT', **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, full_name=full_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('role', 'SUPER_ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('SUPER_ADMIN', 'Super Admin'),
        ('MODULE_ADMIN', 'Module Admin'),
        ('STUDENT', 'Student'),
    )

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    is_active = models.BooleanField(default=False)  # False for students until approved
    is_approved = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    profile_picture = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    module_note = models.TextField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return self.username or self.email

    def save(self, *args, **kwargs):
        if self.role in ['SUPER_ADMIN', 'MODULE_ADMIN']:
            self.is_active = True
            self.is_approved = True
            if self.role == 'SUPER_ADMIN':
                self.is_staff = True
                self.is_superuser = True
        super().save(*args, **kwargs)


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('NEW_STUDENT', 'New Student'),
        ('STUDENT_APPROVED', 'Student Approved'),
        ('STUDENT_REJECTED', 'Student Rejected'),
        ('NEW_QUIZ', 'New Quiz'),
        ('QUIZ_RESULT', 'Quiz Result'),
        ('ANNOUNCEMENT', 'Announcement'),
        ('NEW_CONTENT', 'New Content'),
    )

    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_module = models.ForeignKey('modules.Module', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.recipient.email}"

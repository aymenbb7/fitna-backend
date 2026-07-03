from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from .models import Session, Document, Video, VoiceMessage, Photo
from .serializers import SessionSerializer, DocumentSerializer, VideoSerializer, VoiceMessageSerializer, PhotoSerializer
from modules.models import Module
from users.models import Notification

class IsContentReaderOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
            
        slug = view.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        
        if user.role == 'SUPER_ADMIN':
            return True
            
        if user.role == 'MODULE_ADMIN':
            return getattr(user, 'managed_module', None) == module
            
        if user.role == 'STUDENT':
            if request.method not in permissions.SAFE_METHODS:
                return False
            if not user.is_approved:
                return False
            if not user.enrollments.filter(module=module).exists():
                return False
                
            # Check module settings for the content type
            settings = module.settings
            content_type = getattr(view, 'content_type', None)
            if content_type == 'sessions' and not settings.show_sessions: return False
            if content_type == 'documents' and not settings.show_pdfs: return False
            if content_type == 'videos' and not settings.show_videos: return False
            if content_type == 'voice_messages' and not settings.show_voice: return False
            if content_type == 'photos' and not settings.show_photos: return False
            
            return True
            
        return False

class BaseContentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsContentReaderOrAdmin,)
    content_type = None

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        qs = self.queryset.filter(module=module)
        if self.request.user.role == 'STUDENT':
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        serializer.save(module=module)
        
        # Notify students of new content
        students = module.enrollments.filter(student__is_approved=True).values_list('student', flat=True)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users_to_notify = User.objects.filter(id__in=students)
        
        notifications = [
            Notification(
                recipient=u,
                title="New Content Added",
                message=f"New content has been added to {module.name}.",
                notification_type="NEW_CONTENT",
                related_module=module
            ) for u in users_to_notify
        ]
        Notification.objects.bulk_create(notifications)

class SessionViewSet(BaseContentViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    content_type = 'sessions'

class DocumentViewSet(BaseContentViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    content_type = 'documents'

class VideoViewSet(BaseContentViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    content_type = 'videos'

class VoiceMessageViewSet(BaseContentViewSet):
    queryset = VoiceMessage.objects.all()
    serializer_class = VoiceMessageSerializer
    content_type = 'voice_messages'

class PhotoViewSet(BaseContentViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    content_type = 'photos'

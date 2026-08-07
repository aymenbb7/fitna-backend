from rest_framework import viewsets, generics, views, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Section, Lesson, Document, Video, VoiceMessage, Photo, Session
from .serializers import (
    SectionSerializer, LessonSerializer,
    DocumentSerializer, VideoSerializer, VoiceMessageSerializer,
    PhotoSerializer, SessionSerializer,
)
from modules.models import Module
from users.models import Notification
from core.permissions import IsSuperAdmin, IsModuleOwner


class IsModuleAdminOrSuperAdmin(permissions.BasePermission):
    """Allow SUPER_ADMIN always; allow MODULE_ADMIN only for their own module."""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == 'SUPER_ADMIN':
            return True
        if user.role == 'MODULE_ADMIN':
            slug = view.kwargs.get('slug')
            if not slug:
                return False
            try:
                managed = user.managed_module
                return managed.slug == slug
            except Exception:
                return False
        return False


class IsContentReaderOrAdmin(permissions.BasePermission):
    """
    SUPER_ADMIN / MODULE_ADMIN (owner): full access.
    STUDENT: read-only if enrolled and content type enabled.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        slug = view.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)

        if user.role == 'SUPER_ADMIN':
            return True

        if user.role == 'MODULE_ADMIN':
            try:
                return user.managed_module.slug == slug
            except Exception:
                return False

        if user.role == 'STUDENT':
            if request.method not in permissions.SAFE_METHODS:
                return False
            if not user.is_approved:
                return False
            if not user.enrollments.filter(module=module).exists():
                return False
            try:
                settings_obj = module.settings
                content_type = getattr(view, 'content_type', None)
                if content_type == 'sessions' and not settings_obj.show_sessions:
                    return False
                if content_type == 'documents' and not settings_obj.show_pdfs:
                    return False
                if content_type == 'videos' and not settings_obj.show_videos:
                    return False
                if content_type == 'voice_messages' and not settings_obj.show_voice:
                    return False
                if content_type == 'photos' and not settings_obj.show_photos:
                    return False
            except Exception:
                pass
            return True

        return False


# ─── Section views ─────────────────────────────────────────────────────────

class SectionListCreateView(generics.ListCreateAPIView):
    serializer_class = SectionSerializer
    permission_classes = (IsModuleAdminOrSuperAdmin,)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        return Section.objects.filter(module=module).prefetch_related(
            'lessons',
            'lessons__documents',
            'lessons__videos',
            'lessons__voice_messages',
            'lessons__photos',
            'lessons__sessions',
        )

    def perform_create(self, serializer):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        serializer.save(module=module)


class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SectionSerializer
    permission_classes = (IsModuleAdminOrSuperAdmin,)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        return Section.objects.filter(module=module)

    def get_object(self):
        queryset = self.get_queryset()
        section_id = self.kwargs.get('section_id')
        return get_object_or_404(queryset, id=section_id)


# ─── Lesson views ───────────────────────────────────────────────────────────

class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = (IsModuleAdminOrSuperAdmin,)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Lesson.objects.filter(section__module__slug=slug)

    def perform_create(self, serializer):
        # Validate section belongs to this module
        slug = self.kwargs.get('slug')
        section = serializer.validated_data.get('section')
        if section.module.slug != slug:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Section does not belong to this module.")
        serializer.save()


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = (IsModuleAdminOrSuperAdmin,)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Lesson.objects.filter(section__module__slug=slug)

    def get_object(self):
        queryset = self.get_queryset()
        lesson_id = self.kwargs.get('lesson_id')
        return get_object_or_404(queryset, id=lesson_id)


# ─── Content viewsets (Document, Video, etc.) ───────────────────────────────

class BaseContentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsContentReaderOrAdmin,)
    content_type = None

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        qs = self.queryset.filter(lesson__section__module=module)
        if self.request.user.role == 'STUDENT':
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)

        # Validate lesson belongs to this module (if provided)
        lesson = serializer.validated_data.get('lesson')
        if lesson and lesson.section.module != module:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Lesson does not belong to this module.")

        obj = serializer.save()

        # Notify enrolled students of new content
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            student_ids = module.enrollments.filter(
                student__is_approved=True
            ).values_list('student', flat=True)
            users_to_notify = User.objects.filter(id__in=student_ids)
            notifications = [
                Notification(
                    recipient=u,
                    title="New Content Added",
                    message=f"New content has been added to {module.name}.",
                    notification_type="NEW_CONTENT",
                    related_module=module,
                ) for u in users_to_notify
            ]
            Notification.objects.bulk_create(notifications)
        except Exception:
            pass


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


class SessionViewSet(BaseContentViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    content_type = 'sessions'

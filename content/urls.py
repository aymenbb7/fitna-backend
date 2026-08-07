from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SectionListCreateView, SectionDetailView,
    LessonListCreateView, LessonDetailView,
    DocumentViewSet, VideoViewSet, VoiceMessageViewSet, PhotoViewSet, SessionViewSet,
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'voice', VoiceMessageViewSet, basename='voice_message')
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'sessions', SessionViewSet, basename='session')

urlpatterns = [
    # Sections
    path('sections/', SectionListCreateView.as_view(), name='section-list-create'),
    path('sections/<int:section_id>/', SectionDetailView.as_view(), name='section-detail'),

    # Lessons
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:lesson_id>/', LessonDetailView.as_view(), name='lesson-detail'),

    # Content resources
    path('', include(router.urls)),
]

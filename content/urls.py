from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionViewSet, DocumentViewSet, VideoViewSet, VoiceMessageViewSet, PhotoViewSet

router = DefaultRouter()
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'voice', VoiceMessageViewSet, basename='voice_message')
router.register(r'photos', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls)),
]

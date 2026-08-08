from django.urls import path
from .views import UploadMediaView, CloudinaryConfigDebugView

urlpatterns = [
    path('', UploadMediaView.as_view(), name='upload_media'),
    path('debug-config/', CloudinaryConfigDebugView.as_view(), name='cloudinary_debug'),
]

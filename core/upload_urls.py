from django.urls import path
from .views import UploadMediaView, StorageConfigDebugView

urlpatterns = [
    path('', UploadMediaView.as_view(), name='upload_media'),
    path('debug-config/', StorageConfigDebugView.as_view(), name='storage_debug'),
]

from django.urls import path
from .views import UploadMediaView

urlpatterns = [
    path('', UploadMediaView.as_view(), name='upload_media'),
]

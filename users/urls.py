from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, CustomTokenObtainPairView, MeView, MyNotificationsView, MarkNotificationsReadView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('notifications/', MyNotificationsView.as_view(), name='my_notifications'),
    path('notifications/read/', MarkNotificationsReadView.as_view(), name='mark_notifications_read'),
]

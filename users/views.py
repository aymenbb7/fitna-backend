from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User registered successfully",
            "is_approved": user.is_approved
        }, status=status.HTTP_201_CREATED)

import traceback
import sys

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            if not serializer.is_valid():
                # Check for database connection issues in serializer validation
                errors = serializer.errors
                if 'non_field_errors' in errors and any('database' in str(e).lower() or 'connection' in str(e).lower() for e in errors['non_field_errors']):
                    return Response(
                        {"detail": "تعذر الاتصال بقاعدة البيانات. يرجى مراجعة حالة الخادم."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                return Response(
                    {"detail": "بيانات الدخول غير صحيحة. يرجى المحاولة مرة أخرى.", "errors": errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except Exception as e:
            err_str = str(e).lower()
            if 'connection' in err_str or 'operationalerror' in err_str or 'database' in err_str or 'tenant' in err_str:
                return Response(
                    {"detail": "تعذر الاتصال بقاعدة البيانات. يرجى مراجعة حالة الخادم."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            return Response(
                {"detail": "حدث خطأ أثناء تسجيل الدخول. يرجى المحاولة مرة أخرى.", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class MeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        data = request.data

        # Explicitly ignore email or role changes for security
        allowed_fields = ['full_name', 'phone_number', 'age', 'profile_picture']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])

        # Handle password change
        if 'current_password' in data and 'new_password' in data:
            if not user.check_password(data['current_password']):
                return Response({'error': 'كلمة المرور الحالية غير صحيحة'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(data['new_password'])

        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)

from users.models import Notification

class MyNotificationsView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:50]
        data = []
        for n in notifications:
            data.append({
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "is_read": n.is_read,
                "created_at": n.created_at,
                "sender_name": n.sender.full_name if n.sender else None
            })
        return Response(data)

class MarkNotificationsReadView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({"status": "success"})

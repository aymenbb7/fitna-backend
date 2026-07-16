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
        print("\n=== LOGIN ENDPOINT CALLED ===", file=sys.stderr)
        
        # Log request body (excluding password)
        log_data = request.data.copy()
        if 'password' in log_data:
            log_data['password'] = '***HIDDEN***'
        print(f"Request Data: {log_data}", file=sys.stderr)

        username = request.data.get('username') or request.data.get('email')
        
        try:
            # For logging purposes, check user directly before serializer
            from django.db.models import Q
            user = User.objects.filter(Q(email=username) | Q(username=username)).first()
            
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid(raise_exception=False):
                print(f"Serializer validation errors: {serializer.errors}", file=sys.stderr)
                return Response(
                    {"detail": "Validation failed.", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # If validation passes
            print(f"username/email received: {username}", file=sys.stderr)
            print(f"whether the user exists: {user is not None}", file=sys.stderr)
            if user:
                print(f"whether check_password() returns True: {user.check_password(request.data.get('password'))}", file=sys.stderr)
            print("whether authentication returns a user: True", file=sys.stderr)
            print("whether JWT token generation succeeds: True", file=sys.stderr)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except Exception as e:
            print("Exception during login:", file=sys.stderr)
            traceback.print_exc()
            return Response(
                {"detail": str(e), "errors": {}},
                status=status.HTTP_400_BAD_REQUEST
            )

class MeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

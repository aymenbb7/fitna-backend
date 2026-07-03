from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from modules.models import Module, Enrollment
from users.models import Notification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    enrolled_modules = serializers.SerializerMethodField()
    unread_notifications_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'role', 'is_approved', 'profile_picture', 'phone_number', 'age', 'enrolled_modules', 'unread_notifications_count')

    def get_enrolled_modules(self, obj):
        if obj.role != 'STUDENT':
            return []
        enrollments = Enrollment.objects.filter(student=obj, module__is_active=True)
        return [{
            "slug": e.module.slug,
            "name": e.module.name,
            "icon": e.module.icon,
            "color_primary": e.module.color_primary
        } for e in enrollments]

    def get_unread_notifications_count(self, obj):
        return Notification.objects.filter(recipient=obj, is_read=False).count()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    module_slug = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name', 'phone_number', 'age', 'module_slug')

    def create(self, validated_data):
        module_slug = validated_data.pop('module_slug')
        password = validated_data.pop('password')
        
        try:
            module = Module.objects.get(slug=module_slug, is_active=True)
        except Module.DoesNotExist:
            raise serializers.ValidationError({"module_slug": "Module does not exist or is inactive."})

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        Enrollment.objects.create(student=user, module=module, is_primary=True)

        # Notify module admin
        if module.admin:
            Notification.objects.create(
                recipient=module.admin,
                title="New Student Registration",
                message=f"{user.full_name} has registered for {module.name} and is waiting for approval.",
                notification_type="NEW_STUDENT",
                related_module=module
            )

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        if self.user.role == 'STUDENT' and not self.user.is_approved:
            raise serializers.ValidationError({"detail": "Account is pending approval."})
            
        data['role'] = self.user.role
        data['full_name'] = self.user.full_name
        
        if self.user.role == 'STUDENT':
            enrollments = Enrollment.objects.filter(student=self.user, module__is_active=True)
            data['enrolled_modules'] = [{
                "slug": e.module.slug,
                "name": e.module.name,
                "icon": e.module.icon,
                "color_primary": e.module.color_primary
            } for e in enrollments]
        else:
            data['enrolled_modules'] = []

        return data

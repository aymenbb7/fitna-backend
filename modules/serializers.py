from rest_framework import serializers
from .models import Module, ModuleSettings, Enrollment
from django.contrib.auth import get_user_model

User = get_user_model()

class ModuleSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleSettings
        fields = ('show_sessions', 'show_pdfs', 'show_videos', 'show_voice', 'show_photos', 'show_quizzes', 'show_schedule')

class ModuleSerializer(serializers.ModelSerializer):
    settings = ModuleSettingsSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ('id', 'name', 'slug', 'description', 'icon', 'background_theme', 'is_active', 'display_order', 'cover_image_url', 'color_primary', 'settings')

class StudentListSerializer(serializers.ModelSerializer):
    enrolled_at = serializers.SerializerMethodField()
    is_primary = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'profile_picture', 'phone_number', 'age', 'module_note', 'is_approved', 'enrolled_at', 'is_primary')

    def get_enrolled_at(self, obj):
        module_slug = self.context.get('module_slug')
        enrollment = obj.enrollments.filter(module__slug=module_slug).first()
        return enrollment.enrolled_at if enrollment else None

    def get_is_primary(self, obj):
        module_slug = self.context.get('module_slug')
        enrollment = obj.enrollments.filter(module__slug=module_slug).first()
        return enrollment.is_primary if enrollment else False

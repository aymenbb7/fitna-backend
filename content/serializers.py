from rest_framework import serializers
from .models import Section, Lesson, Document, Video, VoiceMessage, Photo, Session


def is_valid_url(value):
    """Return True if value is a real HTTP/HTTPS URL, not a local path."""
    if not value:
        return False
    s = str(value).strip()
    return s.startswith('http://') or s.startswith('https://')


class DocumentSerializer(serializers.ModelSerializer):
    effective_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = '__all__'

    def get_effective_url(self, obj):
        # Prefer explicit URL field
        if is_valid_url(obj.file_url):
            return obj.file_url
        # Then FileField — in production this is a Cloudinary URL if uploaded via Cloudinary
        if obj.document_file and is_valid_url(obj.document_file.name):
            return obj.document_file.name
        if obj.document_file:
            name = str(obj.document_file)
            if is_valid_url(name):
                return name
            try:
                return obj.document_file.url
            except Exception:
                pass
        return None


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class VoiceMessageSerializer(serializers.ModelSerializer):
    effective_url = serializers.SerializerMethodField()

    class Meta:
        model = VoiceMessage
        fields = '__all__'

    def get_effective_url(self, obj):
        if is_valid_url(obj.audio_url):
            return obj.audio_url
        if obj.audio_file and is_valid_url(obj.audio_file.name):
            return obj.audio_file.name
        if obj.audio_file:
            name = str(obj.audio_file)
            if is_valid_url(name):
                return name
            try:
                return obj.audio_file.url
            except Exception:
                pass
        return None


class PhotoSerializer(serializers.ModelSerializer):
    effective_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = '__all__'

    def get_effective_url(self, obj):
        if is_valid_url(obj.photo_url):
            return obj.photo_url
        if obj.image_file and is_valid_url(obj.image_file.name):
            return obj.image_file.name
        if obj.image_file:
            name = str(obj.image_file)
            if is_valid_url(name):
                return name
            try:
                return obj.image_file.url
            except Exception:
                pass
        return None


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    voice_messages = VoiceMessageSerializer(many=True, read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    sessions = SessionSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ('module',)


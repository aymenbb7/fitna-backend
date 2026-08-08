from rest_framework import serializers
from .models import Section, Lesson, Document, Video, VoiceMessage, Photo, Session


def get_http_url(value):
    """Return value only if it is an absolute HTTP/HTTPS URL. Otherwise return None."""
    if not value:
        return None
    s = str(value).strip()
    if s.startswith('http://') or s.startswith('https://'):
        return s
    return None


class DocumentSerializer(serializers.ModelSerializer):
    effective_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = '__all__'

    def get_effective_url(self, obj):
        # 1. Prefer explicit file_url (a proper URLField)
        url = get_http_url(obj.file_url)
        if url:
            return url
        # 2. Check if document_file name is already a full URL (Cloudinary sets this when
        #    files are uploaded via cloudinary_storage)
        if obj.document_file:
            url = get_http_url(obj.document_file.name)
            if url:
                return url
            # 3. Ask the storage backend for the URL (works correctly when storage is Cloudinary)
            #    But only trust the result if it is an absolute URL
            try:
                backend_url = obj.document_file.url
                url = get_http_url(backend_url)
                if url:
                    return url
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
        url = get_http_url(obj.audio_url)
        if url:
            return url
        if obj.audio_file:
            url = get_http_url(obj.audio_file.name)
            if url:
                return url
            try:
                backend_url = obj.audio_file.url
                url = get_http_url(backend_url)
                if url:
                    return url
            except Exception:
                pass
        return None


class PhotoSerializer(serializers.ModelSerializer):
    effective_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = '__all__'

    def get_effective_url(self, obj):
        url = get_http_url(obj.photo_url)
        if url:
            return url
        if obj.image_file:
            url = get_http_url(obj.image_file.name)
            if url:
                return url
            try:
                backend_url = obj.image_file.url
                url = get_http_url(backend_url)
                if url:
                    return url
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


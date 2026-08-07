from rest_framework import serializers
from .models import Section, Lesson, Document, Video, VoiceMessage, Photo, Session


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class VoiceMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceMessage
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'


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

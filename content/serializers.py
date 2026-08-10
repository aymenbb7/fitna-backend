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
    quizzes = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = '__all__'

    def get_quizzes(self, obj):
        from quizzes.models import Quiz
        qs = Quiz.objects.filter(lesson=obj, is_active=True)
        return TrialQuizSerializer(qs, many=True).data


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ('module',)


# ─── Trial / Free Preview serializers ────────────────────────────────────────

class TrialAnswerChoiceSerializer(serializers.ModelSerializer):
    """Exposes answer choices WITHOUT revealing which is correct."""
    class Meta:
        from quizzes.models import AnswerChoice
        model = AnswerChoice
        fields = ('id', 'text', 'display_order')


class TrialQuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions in the free trial — hides correct answers."""
    choices = TrialAnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        from quizzes.models import Question
        model = Question
        fields = ('id', 'text', 'question_type', 'points', 'display_order', 'choices')


class TrialQuizSerializer(serializers.ModelSerializer):
    """Active quiz with questions/choices for the trial page."""
    questions = TrialQuestionSerializer(many=True, read_only=True)
    questions_count = serializers.SerializerMethodField()

    class Meta:
        from quizzes.models import Quiz
        model = Quiz
        fields = ('id', 'title', 'description', 'time_limit_minutes', 'passing_score',
                  'show_results_immediately', 'questions', 'questions_count')

    def get_questions_count(self, obj):
        return obj.questions.count()


class TrialLessonSerializer(serializers.ModelSerializer):
    """
    Full lesson serializer for the free-trial endpoint.
    Includes all media AND active quizzes attached to this lesson.
    Only active content is included.
    """
    documents = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    voice_messages = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()
    quizzes = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'description', 'display_order',
                  'documents', 'videos', 'voice_messages', 'photos',
                  'sessions', 'quizzes')

    def get_documents(self, obj):
        qs = obj.documents.filter(is_active=True)
        return DocumentSerializer(qs, many=True).data

    def get_videos(self, obj):
        qs = obj.videos.filter(is_active=True)
        return VideoSerializer(qs, many=True).data

    def get_voice_messages(self, obj):
        qs = obj.voice_messages.filter(is_active=True)
        return VoiceMessageSerializer(qs, many=True).data

    def get_photos(self, obj):
        qs = obj.photos.filter(is_active=True)
        return PhotoSerializer(qs, many=True).data

    def get_sessions(self, obj):
        qs = obj.sessions.filter(is_active=True)
        return SessionSerializer(qs, many=True).data

    def get_quizzes(self, obj):
        from quizzes.models import Quiz
        qs = Quiz.objects.filter(lesson=obj, is_active=True)
        return TrialQuizSerializer(qs, many=True).data


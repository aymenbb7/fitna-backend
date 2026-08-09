from rest_framework import serializers
from .models import Quiz, Question, AnswerChoice, QuizAttempt, StudentAnswer


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ('id', 'text', 'is_correct', 'display_order')
        # is_correct is always readable — the view strips it for students at submission time

class AdminAnswerChoiceSerializer(serializers.ModelSerializer):
    """Always exposes is_correct — used in admin quiz-builder endpoints."""
    class Meta:
        model = AnswerChoice
        fields = ('id', 'text', 'is_correct', 'display_order')


class QuestionSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'points', 'display_order', 'explanation', 'choices')


class AdminQuestionSerializer(serializers.ModelSerializer):
    """Admin serializer that exposes is_correct on choices."""
    choices = AdminAnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'points', 'display_order', 'explanation', 'choices')


class QuizSerializer(serializers.ModelSerializer):
    questions = AdminQuestionSerializer(many=True, read_only=True)
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = '__all__'
        read_only_fields = ('module',)

    def get_questions_count(self, obj):
        return obj.questions.count()


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ('question', 'selected_choices', 'is_correct', 'points_earned')

class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = StudentAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = '__all__'

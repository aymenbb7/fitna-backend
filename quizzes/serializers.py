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
    """Admin serializer that supports nested creation and exposes is_correct on choices."""
    choices = AdminAnswerChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'points', 'display_order', 'explanation', 'choices')

    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        for i, choice_data in enumerate(choices_data):
            # Ensure display_order is set
            choice_data.setdefault('display_order', i)
            AnswerChoice.objects.create(question=question, **choice_data)
        return question


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

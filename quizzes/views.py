from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Quiz, Question, AnswerChoice, QuizAttempt, StudentAnswer
from .serializers import QuizSerializer, QuestionSerializer, QuizAttemptSerializer
from modules.models import Module
from content.views import IsContentReaderOrAdmin
from core.permissions import IsModuleOwner, IsSuperAdmin
from users.models import Notification
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Max, Min

User = get_user_model()

class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = (IsContentReaderOrAdmin,)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        qs = Quiz.objects.filter(module=module)
        if self.request.user.role == 'STUDENT':
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        quiz = serializer.save(module=module)
        
        if quiz.is_active:
            self._notify_students(module, quiz)

    def perform_update(self, serializer):
        quiz = serializer.save()
        if quiz.is_active and not getattr(quiz, '_was_active_before', False):
            self._notify_students(quiz.module, quiz)

    def _notify_students(self, module, quiz):
        students = module.enrollments.filter(student__is_approved=True).values_list('student', flat=True)
        users_to_notify = User.objects.filter(id__in=students)
        notifications = [
            Notification(
                recipient=u,
                title="New Quiz Available",
                message=f"A new quiz '{quiz.title}' is available in {module.name}.",
                notification_type="NEW_QUIZ",
                related_module=module
            ) for u in users_to_notify
        ]
        Notification.objects.bulk_create(notifications)

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = (IsModuleOwner | IsSuperAdmin,)

    def get_queryset(self):
        return Question.objects.filter(quiz_id=self.kwargs.get('quiz_pk'))

    def perform_create(self, serializer):
        quiz = get_object_or_404(Quiz, pk=self.kwargs.get('quiz_pk'))
        serializer.save(quiz=quiz)

class IsQuizParticipant(IsContentReaderOrAdmin):
    def has_permission(self, request, view):
        # We need to temporarily pretend it's a GET request to bypass the SAFE_METHODS check in the parent
        # or we just reimplement the check specifically for quizzes.
        user = request.user
        if not user or not user.is_authenticated: return False
        if user.role in ['SUPER_ADMIN', 'MODULE_ADMIN']: return True
        if user.role == 'STUDENT':
            if not user.is_approved: return False
            slug = view.kwargs.get('slug')
            module = get_object_or_404(Module, slug=slug)
            if not user.enrollments.filter(module=module).exists(): return False
            if not module.settings.show_quizzes: return False
            return True
        return False

class StartQuizAttemptView(views.APIView):
    permission_classes = (IsQuizParticipant,)

    def post(self, request, slug, pk):
        quiz = get_object_or_404(Quiz, pk=pk, module__slug=slug, is_active=True)
        user = request.user
        
        if user.role != 'STUDENT':
            return Response({"error": "Only students can take quizzes."}, status=status.HTTP_403_FORBIDDEN)
            
        attempts_count = QuizAttempt.objects.filter(quiz=quiz, student=user).count()
        if quiz.max_attempts > 0 and attempts_count >= quiz.max_attempts:
            return Response({"error": "Max attempts reached."}, status=status.HTTP_400_BAD_REQUEST)
            
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=user,
            attempt_number=attempts_count + 1
        )
        
        # Return questions without correct answers
        serializer = QuizSerializer(quiz)
        data = serializer.data
        # Remove is_correct from choices in the response
        for q in data['questions']:
            for c in q['choices']:
                c.pop('is_correct', None)
                
        return Response({
            "attempt_id": attempt.id,
            "quiz": data
        })

class SubmitQuizAttemptView(views.APIView):
    permission_classes = (IsQuizParticipant,)

    def post(self, request, slug, pk):
        quiz = get_object_or_404(Quiz, pk=pk, module__slug=slug)
        user = request.user
        attempt_id = request.data.get('attempt_id')
        answers_data = request.data.get('answers', [])
        
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=user, quiz=quiz)
        if attempt.is_completed:
            return Response({"error": "Attempt already completed."}, status=status.HTTP_400_BAD_REQUEST)
            
        total_points_possible = sum([q.points for q in quiz.questions.all()])
        total_points_earned = 0
        
        results = []
        
        for answer in answers_data:
            question_id = answer.get('question_id')
            choice_ids = answer.get('choice_ids', [])
            
            try:
                question = Question.objects.get(id=question_id, quiz=quiz)
            except Question.DoesNotExist:
                continue
                
            correct_choices = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
            selected_choices = set(choice_ids)
            
            is_correct = False
            points_earned = 0
            
            if question.question_type == 'MCQ' or question.question_type == 'TRUE_FALSE':
                if len(selected_choices) == 1 and selected_choices == correct_choices:
                    is_correct = True
            elif question.question_type == 'MULTI':
                if selected_choices == correct_choices:
                    is_correct = True
                    
            if is_correct:
                points_earned = question.points
                total_points_earned += points_earned
                
            student_answer = StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                is_correct=is_correct,
                points_earned=points_earned
            )
            student_answer.selected_choices.set(choice_ids)
            
            results.append({
                "question_id": question.id,
                "is_correct": is_correct,
                "points_earned": points_earned,
                "explanation": question.explanation if quiz.show_results_immediately else ""
            })
            
        score = (total_points_earned / total_points_possible * 100) if total_points_possible > 0 else 0
        
        attempt.completed_at = timezone.now()
        attempt.score = score
        attempt.total_points_earned = total_points_earned
        attempt.total_points_possible = total_points_possible
        attempt.is_completed = True
        attempt.save()
        
        passed = score >= quiz.passing_score
        
        # Notify student of result
        Notification.objects.create(
            recipient=user,
            title="Quiz Result",
            message=f"You scored {score:.1f}% on '{quiz.title}'. You {'passed' if passed else 'failed'}.",
            notification_type="QUIZ_RESULT",
            related_module=quiz.module
        )

        response_data = {
            "score": score,
            "passed": passed,
            "total_points_earned": total_points_earned,
            "total_points_possible": total_points_possible,
        }
        
        if quiz.show_results_immediately:
            response_data["results"] = results
            
        return Response(response_data)

class QuizResultsAdminView(views.APIView):
    permission_classes = (IsModuleOwner | IsSuperAdmin,)

    def get(self, request, slug, pk):
        quiz = get_object_or_404(Quiz, pk=pk, module__slug=slug)
        attempts = QuizAttempt.objects.filter(quiz=quiz, is_completed=True).select_related('student')
        
        student_results = []
        for a in attempts:
            student_results.append({
                "name": a.student.full_name,
                "score": a.score,
                "passed": a.score >= quiz.passing_score if a.score is not None else False,
                "attempt_number": a.attempt_number,
                "completed_at": a.completed_at,
                "time_taken_seconds": (a.completed_at - a.started_at).total_seconds() if a.completed_at else 0
            })
            
        question_stats = []
        for q in quiz.questions.all():
            total_answers = StudentAnswer.objects.filter(question=q, attempt__is_completed=True).count()
            correct_answers = StudentAnswer.objects.filter(question=q, attempt__is_completed=True, is_correct=True).count()
            
            wrong_answers = total_answers - correct_answers
            correct_rate = (correct_answers / total_answers * 100) if total_answers > 0 else 0
            wrong_rate = (wrong_answers / total_answers * 100) if total_answers > 0 else 0
            
            most_common_wrong = None
            if wrong_answers > 0:
                most_frequent_choice = StudentAnswer.objects.filter(
                    question=q, attempt__is_completed=True, is_correct=False
                ).values('selected_choices__text').annotate(
                    count=Count('selected_choices')
                ).order_by('-count').first()
                if most_frequent_choice and most_frequent_choice['selected_choices__text']:
                    most_common_wrong = most_frequent_choice['selected_choices__text']
                    
            question_stats.append({
                "question_text": q.text,
                "correct_rate": correct_rate,
                "wrong_rate": wrong_rate,
                "most_common_wrong": most_common_wrong
            })
            
        avg_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
        pass_count = sum(1 for a in attempts if a.score and a.score >= quiz.passing_score)
        total_attempts = attempts.count()
        pass_rate = (pass_count / total_attempts * 100) if total_attempts > 0 else 0
        
        highest_score = attempts.aggregate(Max('score'))['score__max'] or 0
        lowest_score = attempts.aggregate(Min('score'))['score__min'] or 0

        return Response({
            "overall_stats": {
                "average_score": avg_score,
                "pass_rate": pass_rate,
                "highest_score": highest_score,
                "lowest_score": lowest_score,
                "total_attempts": total_attempts
            },
            "student_results": student_results,
            "question_stats": question_stats
        })

class QuizMyResultsView(views.APIView):
    permission_classes = (IsContentReaderOrAdmin,)

    def get(self, request, slug, pk):
        quiz = get_object_or_404(Quiz, pk=pk, module__slug=slug)
        attempts = QuizAttempt.objects.filter(quiz=quiz, student=request.user, is_completed=True)
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)

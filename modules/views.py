from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Max, Min

from .models import Module, ModuleSettings, Enrollment
from .serializers import ModuleSerializer, StudentListSerializer, ModuleSettingsSerializer
from core.permissions import IsModuleOwner, IsSuperAdmin
from users.models import Notification
from quizzes.models import QuizAttempt

User = get_user_model()

class ModuleListView(generics.ListAPIView):
    queryset = Module.objects.filter(is_active=True).order_by('display_order')
    serializer_class = ModuleSerializer
    permission_classes = (AllowAny,)

class ModuleDetailView(generics.RetrieveAPIView):
    queryset = Module.objects.filter(is_active=True)
    serializer_class = ModuleSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPER_ADMIN':
            return Module.objects.all()
        elif user.role == 'MODULE_ADMIN':
            return Module.objects.filter(id=getattr(user, 'managed_module', None).id if hasattr(user, 'managed_module') else None)
        else:
            # Student
            return Module.objects.filter(enrollments__student=user, is_active=True)

class ModuleDashboardView(views.APIView):
    permission_classes = (IsAuthenticated, IsModuleOwner | IsSuperAdmin)

    def get(self, request, slug):
        module = get_object_or_404(Module, slug=slug)
        total_students = Enrollment.objects.filter(module=module, student__is_approved=True).count()
        pending_students = Enrollment.objects.filter(module=module, student__is_approved=False).count()
        
        return Response({
            "total_students": total_students,
            "pending_approvals": pending_students,
            "sessions_count": module.sessions.count(),
            "documents_count": module.documents.count(),
            "videos_count": module.videos.count(),
            "voice_messages_count": module.voice_messages.count(),
            "photos_count": module.photos.count(),
            "quizzes_count": module.quizzes.count()
        })

class StudentListView(generics.ListAPIView):
    serializer_class = StudentListSerializer
    permission_classes = (IsAuthenticated, IsModuleOwner | IsSuperAdmin)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return User.objects.filter(enrollments__module__slug=slug, is_approved=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['module_slug'] = self.kwargs.get('slug')
        return context

class PendingStudentListView(generics.ListAPIView):
    serializer_class = StudentListSerializer
    permission_classes = (IsAuthenticated, IsModuleOwner | IsSuperAdmin)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return User.objects.filter(enrollments__module__slug=slug, is_approved=False)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['module_slug'] = self.kwargs.get('slug')
        return context

class ApproveStudentView(views.APIView):
    permission_classes = (IsAuthenticated, IsModuleOwner | IsSuperAdmin)

    def post(self, request, slug, pk):
        student = get_object_or_404(User, pk=pk, role='STUDENT')
        enrollment = get_object_or_404(Enrollment, student=student, module__slug=slug)
        
        student.is_approved = True
        student.is_active = True
        student.save()
        
        Notification.objects.create(
            recipient=student,
            title="Registration Approved",
            message=f"Your registration for {enrollment.module.name} has been approved. Welcome!",
            notification_type="STUDENT_APPROVED",
            related_module=enrollment.module
        )
        
        return Response({"message": "Student approved successfully."})

class RejectStudentView(views.APIView):
    permission_classes = (IsAuthenticated, IsModuleOwner | IsSuperAdmin)

    def post(self, request, slug, pk):
        student = get_object_or_404(User, pk=pk, role='STUDENT')
        enrollment = get_object_or_404(Enrollment, student=student, module__slug=slug)
        module = enrollment.module
        
        enrollment.delete()
        if not Enrollment.objects.filter(student=student).exists():
            student.delete()
            
        Notification.objects.create(
            recipient=student,
            title="Registration Rejected",
            message=f"Your registration for {module.name} has been rejected.",
            notification_type="STUDENT_REJECTED",
            related_module=module
        )
            
        return Response({"message": "Student rejected and enrollment removed."})

class RemoveStudentView(views.APIView):
    permission_classes = (IsAuthenticated, IsModuleOwner | IsSuperAdmin)

    def delete(self, request, slug, pk):
        student = get_object_or_404(User, pk=pk, role='STUDENT')
        enrollment = get_object_or_404(Enrollment, student=student, module__slug=slug)
        enrollment.delete()
        
        return Response({"message": "Student removed from module."}, status=status.HTTP_204_NO_CONTENT)

class ModuleSettingsUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ModuleSettingsSerializer
    permission_classes = (IsAuthenticated, IsModuleOwner | IsSuperAdmin)

    def get_object(self):
        slug = self.kwargs.get('slug')
        module = get_object_or_404(Module, slug=slug)
        return module.settings

class ModuleAnalyticsView(views.APIView):
    permission_classes = (IsAuthenticated, IsModuleOwner | IsSuperAdmin)

    def get(self, request, slug):
        module = get_object_or_404(Module, slug=slug)
        
        total_students = Enrollment.objects.filter(module=module, student__is_approved=True).count()
        pending_students = Enrollment.objects.filter(module=module, student__is_approved=False).count()
        
        recent_students = User.objects.filter(
            enrollments__module=module, 
            is_approved=True
        ).order_by('-date_joined')[:5]
        
        # Quiz performance
        quizzes = module.quizzes.filter(is_active=True).annotate(
            avg_score=Avg('attempts__score')
        )
        
        best_quiz = quizzes.order_by('-avg_score').first()
        worst_quiz = quizzes.order_by('avg_score').first()

        return Response({
            "total_students": total_students,
            "pending_students": pending_students,
            "content_summary": {
                "sessions_count": module.sessions.filter(is_active=True).count(),
                "documents_count": module.documents.filter(is_active=True).count(),
                "videos_count": module.videos.filter(is_active=True).count(),
                "voice_count": module.voice_messages.filter(is_active=True).count(),
                "photos_count": module.photos.filter(is_active=True).count(),
                "quizzes_count": module.quizzes.filter(is_active=True).count(),
            },
            "recent_students": [
                {"id": s.id, "full_name": s.full_name, "email": s.email} for s in recent_students
            ],
            "quiz_performance": {
                "best_performing_quiz": {"title": best_quiz.title, "avg_score": best_quiz.avg_score} if best_quiz else None,
                "worst_performing_quiz": {"title": worst_quiz.title, "avg_score": worst_quiz.avg_score} if worst_quiz else None,
            }
        })

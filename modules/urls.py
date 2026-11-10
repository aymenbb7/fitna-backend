from django.urls import path, include
from .views import (
    ModuleListView, ModuleDetailView, ModuleDashboardView,
    StudentListView, PendingStudentListView, ApproveStudentView,
    RejectStudentView, RemoveStudentView, ModuleSettingsUpdateView, ModuleAnalyticsView,
    ModuleTrialView
)

urlpatterns = [
    path('', ModuleListView.as_view(), name='module_list'),
    path('<str:slug>/', ModuleDetailView.as_view(), name='module_detail'),
    path('<str:slug>/dashboard/', ModuleDashboardView.as_view(), name='module_dashboard'),
    path('<str:slug>/analytics/', ModuleAnalyticsView.as_view(), name='module_analytics'),
    path('<str:slug>/trial/', ModuleTrialView.as_view(), name='module_trial'),
    
    # Settings
    path('<str:slug>/settings/', ModuleSettingsUpdateView.as_view(), name='module_settings'),
    
    # Students
    path('<str:slug>/students/', StudentListView.as_view(), name='student_list'),
    path('<str:slug>/students/pending/', PendingStudentListView.as_view(), name='pending_student_list'),
    path('<str:slug>/students/<int:pk>/approve/', ApproveStudentView.as_view(), name='approve_student'),
    path('<str:slug>/students/<int:pk>/reject/', RejectStudentView.as_view(), name='reject_student'),
    path('<str:slug>/students/<int:pk>/', RemoveStudentView.as_view(), name='remove_student'),
    
    # Content & Quizzes
    path('<str:slug>/', include('content.urls')),
    path('<str:slug>/quizzes/', include('quizzes.urls')),
]

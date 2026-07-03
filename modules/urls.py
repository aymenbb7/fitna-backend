from django.urls import path, include
from .views import (
    ModuleListView, ModuleDetailView, ModuleDashboardView,
    StudentListView, PendingStudentListView, ApproveStudentView,
    RejectStudentView, RemoveStudentView, ModuleSettingsUpdateView, ModuleAnalyticsView
)

urlpatterns = [
    path('', ModuleListView.as_view(), name='module_list'),
    path('<slug:slug>/', ModuleDetailView.as_view(), name='module_detail'),
    path('<slug:slug>/dashboard/', ModuleDashboardView.as_view(), name='module_dashboard'),
    path('<slug:slug>/analytics/', ModuleAnalyticsView.as_view(), name='module_analytics'),
    
    # Settings
    path('<slug:slug>/settings/', ModuleSettingsUpdateView.as_view(), name='module_settings'),
    
    # Students
    path('<slug:slug>/students/', StudentListView.as_view(), name='student_list'),
    path('<slug:slug>/students/pending/', PendingStudentListView.as_view(), name='pending_student_list'),
    path('<slug:slug>/students/<int:pk>/approve/', ApproveStudentView.as_view(), name='approve_student'),
    path('<slug:slug>/students/<int:pk>/reject/', RejectStudentView.as_view(), name='reject_student'),
    path('<slug:slug>/students/<int:pk>/', RemoveStudentView.as_view(), name='remove_student'),
    
    # Content & Quizzes
    path('<slug:slug>/', include('content.urls')),
    path('<slug:slug>/quizzes/', include('quizzes.urls')),
]

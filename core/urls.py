from django.urls import path
from .views import SuperAdminStatsView, SuperAdminUsersView, SuperAdminAssignModuleAdminView, SuperAdminAddStudentModuleView, SuperAdminModulesView

urlpatterns = [
    path('stats/', SuperAdminStatsView.as_view(), name='superadmin_stats'),
    path('users/', SuperAdminUsersView.as_view(), name='superadmin_users'),
    path('modules/', SuperAdminModulesView.as_view(), name='superadmin_modules'),
    path('modules/<slug:slug>/assign-admin/', SuperAdminAssignModuleAdminView.as_view(), name='superadmin_assign_admin'),
    path('students/<int:pk>/add-module/', SuperAdminAddStudentModuleView.as_view(), name='superadmin_add_student_module'),
]

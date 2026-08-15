from django.urls import path
from .views import (
    SuperAdminStatsView, SuperAdminUsersView, SuperAdminCreateStudentView, 
    SuperAdminAssignModuleAdminView, SuperAdminAddStudentModuleView, 
    SuperAdminModulesView, DashboardStatsView, StudentEnrollmentsView, 
    StudentPaymentsView, UsersExportView, SiteSettingsView, PublicSiteSettingsView,
    SuperAdminUserUpdateView, SuperAdminUserStatusView, SuperAdminUserResetPasswordView,
    SuperAdminCreateModuleAdminView, SuperAdminModuleUpdateView,
    SuperAdminModuleStatsView, SuperAdminUserDeleteView, ModuleAdminCreateStudentView,
    SuperAdminCreateModuleView, SuperAdminModuleDeleteView,
    RepairMediaView
)
from .revenue_views import RevenueStatsView, RevenueExportView
from .notification_views import BroadcastNotificationView, NotificationHistoryView, NotificationDeleteView

urlpatterns = [
    path('repair-media/', RepairMediaView.as_view(), name='repair_media'),
    path('site-settings/', SiteSettingsView.as_view(), name='site_settings'),
    path('stats/', SuperAdminStatsView.as_view(), name='superadmin_stats'),
    
    path('users/', SuperAdminUsersView.as_view(), name='superadmin_users'),
    path('users/export/', UsersExportView.as_view(), name='users_export'),
    path('users/<int:pk>/update/', SuperAdminUserUpdateView.as_view(), name='superadmin_user_update'),
    path('users/<int:pk>/delete/', SuperAdminUserDeleteView.as_view(), name='superadmin_user_delete'),
    path('users/<int:pk>/', SuperAdminUserDeleteView.as_view(), name='superadmin_user_delete_alt'),
    path('users/<int:pk>/status/', SuperAdminUserStatusView.as_view(), name='superadmin_user_status'),
    path('users/<int:pk>/reset-password/', SuperAdminUserResetPasswordView.as_view(), name='superadmin_user_reset_password'),
    
    path('module-admins/create/', SuperAdminCreateModuleAdminView.as_view(), name='superadmin_create_module_admin'),
    
    path('modules/create/', SuperAdminCreateModuleView.as_view(), name='superadmin_create_module'),
    path('modules/', SuperAdminModulesView.as_view(), name='superadmin_modules'),
    path('modules/<str:slug>/', SuperAdminModuleDeleteView.as_view(), name='superadmin_module_delete'),
    path('modules/<str:slug>/stats/', SuperAdminModuleStatsView.as_view(), name='superadmin_module_stats'),
    path('modules/<str:slug>/update/', SuperAdminModuleUpdateView.as_view(), name='superadmin_module_update'),
    path('modules/dashboard-stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('modules/<str:slug>/assign-admin/', SuperAdminAssignModuleAdminView.as_view(), name='superadmin_assign_admin'),
    
    path('students/create/', SuperAdminCreateStudentView.as_view(), name='superadmin_create_student'),
    path('students/create-by-admin/', ModuleAdminCreateStudentView.as_view(), name='module_admin_create_student'),
    path('students/<int:pk>/add-module/', SuperAdminAddStudentModuleView.as_view(), name='superadmin_add_student_module'),
    path('students/<int:pk>/enrollments/', StudentEnrollmentsView.as_view(), name='student_enrollments'),
    path('students/<int:pk>/payments/', StudentPaymentsView.as_view(), name='student_payments'),
    
    # Revenue
    path('revenue/stats/', RevenueStatsView.as_view(), name='revenue_stats'),
    path('revenue/export/', RevenueExportView.as_view(), name='revenue_export'),
    
    # Notifications
    path('notifications/history/', NotificationHistoryView.as_view(), name='notifications_history'),
    path('notifications/broadcast/', BroadcastNotificationView.as_view(), name='notifications_broadcast'),
    path('notifications/<int:pk>/delete/', NotificationDeleteView.as_view(), name='notification_delete'),
]

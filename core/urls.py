from django.urls import path
from .views import (
    SuperAdminStatsView, SuperAdminUsersView, SuperAdminCreateStudentView, 
    SuperAdminAssignModuleAdminView, SuperAdminAddStudentModuleView, 
    SuperAdminModulesView, DashboardStatsView, StudentEnrollmentsView, 
    StudentPaymentsView, UsersExportView, SiteSettingsView, PublicSiteSettingsView,
    SuperAdminUserUpdateView, SuperAdminUserStatusView, SuperAdminUserResetPasswordView,
    SuperAdminCreateModuleAdminView
)
from .revenue_views import RevenueStatsView, RevenueExportView
from .notification_views import BroadcastNotificationView, NotificationHistoryView, NotificationDeleteView

urlpatterns = [
    path('site-settings/', SiteSettingsView.as_view(), name='site_settings'),
    path('public-site-settings/', PublicSiteSettingsView.as_view(), name='public_site_settings'),
    path('stats/', SuperAdminStatsView.as_view(), name='superadmin_stats'),
    
    path('users/', SuperAdminUsersView.as_view(), name='superadmin_users'),
    path('users/export/', UsersExportView.as_view(), name='users_export'),
    path('users/<int:pk>/update/', SuperAdminUserUpdateView.as_view(), name='superadmin_user_update'),
    path('users/<int:pk>/status/', SuperAdminUserStatusView.as_view(), name='superadmin_user_status'),
    path('users/<int:pk>/reset-password/', SuperAdminUserResetPasswordView.as_view(), name='superadmin_user_reset_password'),
    
    path('module-admins/create/', SuperAdminCreateModuleAdminView.as_view(), name='superadmin_create_module_admin'),
    
    path('modules/', SuperAdminModulesView.as_view(), name='superadmin_modules'),
    path('modules/dashboard-stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('modules/<slug:slug>/assign-admin/', SuperAdminAssignModuleAdminView.as_view(), name='superadmin_assign_admin'),
    
    path('students/create/', SuperAdminCreateStudentView.as_view(), name='superadmin_create_student'),
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

from django.urls import path
from .views import SuperAdminStatsView, SuperAdminUsersView, SuperAdminAssignModuleAdminView, SuperAdminAddStudentModuleView, SuperAdminModulesView, DashboardStatsView
from .revenue_views import RevenueStatsView, RevenueExportView
from .notification_views import BroadcastNotificationView, NotificationHistoryView, NotificationDeleteView

urlpatterns = [
    path('stats/', SuperAdminStatsView.as_view(), name='superadmin_stats'),
    path('users/', SuperAdminUsersView.as_view(), name='superadmin_users'),
    path('modules/', SuperAdminModulesView.as_view(), name='superadmin_modules'),
    path('modules/dashboard-stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('modules/<slug:slug>/assign-admin/', SuperAdminAssignModuleAdminView.as_view(), name='superadmin_assign_admin'),
    path('students/<int:pk>/add-module/', SuperAdminAddStudentModuleView.as_view(), name='superadmin_add_student_module'),
    
    # Revenue
    path('revenue/stats/', RevenueStatsView.as_view(), name='revenue_stats'),
    path('revenue/export/', RevenueExportView.as_view(), name='revenue_export'),
    
    # Notifications
    path('notifications/history/', NotificationHistoryView.as_view(), name='notifications_history'),
    path('notifications/broadcast/', BroadcastNotificationView.as_view(), name='notifications_broadcast'),
    path('notifications/<int:pk>/delete/', NotificationDeleteView.as_view(), name='notification_delete'),
]

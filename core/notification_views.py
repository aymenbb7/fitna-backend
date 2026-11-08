from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser, Notification
from modules.models import Module, Enrollment
from django.db.models import Q

class BroadcastNotificationView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.user.role not in ['SUPER_ADMIN', 'MODULE_ADMIN']:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        title = request.data.get('title')
        message = request.data.get('message')
        target_type = request.data.get('target_type') # ALL, ALL_STUDENTS, ALL_MODULE_ADMINS, MODULES, STUDENTS
        target_ids = request.data.get('target_ids', []) # list of module ids or student ids

        if not title or not message or not target_type:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        recipients = CustomUser.objects.none()

        if request.user.role == 'SUPER_ADMIN':
            if target_type == 'ALL':
                recipients = CustomUser.objects.exclude(id=request.user.id)
            elif target_type == 'ALL_STUDENTS':
                recipients = CustomUser.objects.filter(role='STUDENT')
            elif target_type == 'ALL_MODULE_ADMINS':
                recipients = CustomUser.objects.filter(role='MODULE_ADMIN')
            elif target_type == 'MODULES':
                recipients = CustomUser.objects.filter(
                    role='STUDENT', 
                    enrollments__module_id__in=target_ids
                ).distinct()
            elif target_type == 'STUDENTS':
                recipients = CustomUser.objects.filter(id__in=target_ids, role='STUDENT')
                
        elif request.user.role == 'MODULE_ADMIN':
            # Module Admin can only target students in their modules
            my_modules = Module.objects.filter(admin=request.user)
            my_students = CustomUser.objects.filter(
                role='STUDENT',
                enrollments__module__in=my_modules
            ).distinct()

            if target_type == 'ALL_STUDENTS': # Means all THEIR students
                recipients = my_students
            elif target_type == 'STUDENTS':
                # Filter requested student IDs to only those they have access to
                recipients = my_students.filter(id__in=target_ids)
            else:
                return Response({"error": "Invalid target type for module admin"}, status=status.HTTP_403_FORBIDDEN)

        if not recipients.exists():
            return Response({"error": "لم يتم العثور على مستلمين مطابقين."}, status=status.HTTP_400_BAD_REQUEST)

        notifications_to_create = []
        for user in recipients:
            notifications_to_create.append(
                Notification(
                    recipient=user,
                    sender=request.user,
                    title=title,
                    message=message,
                    notification_type='ANNOUNCEMENT'
                )
            )
        
        Notification.objects.bulk_create(notifications_to_create)

        return Response({
            "message": f"Successfully sent notification to {len(notifications_to_create)} users."
        })

class NotificationHistoryView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.role not in ['SUPER_ADMIN', 'MODULE_ADMIN']:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
            
        if request.user.role == 'SUPER_ADMIN':
            sent_notifications = (
                Notification.objects.select_related('recipient', 'sender')
                .order_by('-created_at')[:200]
            )
        else:
            sent_notifications = (
                Notification.objects.filter(sender=request.user)
                .select_related('recipient', 'sender')
                .order_by('-created_at')[:200]
            )
        
        data = []
        for n in sent_notifications:
            try:
                recipient_email = n.recipient.email if n.recipient else "N/A"
            except Exception:
                recipient_email = "N/A"

            try:
                sender_name = n.sender.full_name if n.sender else "System"
            except Exception:
                sender_name = "System"

            data.append({
                "id": n.id,
                "title": n.title or "",
                "message": n.message or "",
                "recipient": recipient_email,
                "type": n.notification_type or "GENERAL",
                "is_read": bool(n.is_read),
                "created_at": n.created_at.isoformat() if hasattr(n.created_at, 'isoformat') else str(n.created_at),
                "sender_name": sender_name
            })
            
        return Response(data)

class NotificationDeleteView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        if request.user.role not in ['SUPER_ADMIN', 'MODULE_ADMIN']:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            if request.user.role == 'SUPER_ADMIN':
                notification = Notification.objects.get(id=pk)
            else:
                notification = Notification.objects.get(id=pk, sender=request.user)
                
            notification.delete()
            return Response({"message": "Notification deleted successfully"})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found or unauthorized to delete"}, status=status.HTTP_404_NOT_FOUND)

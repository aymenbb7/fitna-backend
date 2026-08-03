from rest_framework import permissions
import cloudinary.uploader
from rest_framework import views, status, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSuperAdmin
from django.contrib.auth import get_user_model
from modules.models import Module, Enrollment
from users.serializers import UserSerializer
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()

class UploadMediaView(views.APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        if request.user.role not in ['SUPER_ADMIN', 'MODULE_ADMIN']:
            return Response({"error": "Not authorized to upload media"}, status=status.HTTP_403_FORBIDDEN)
            
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            import requests
            import os
            cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
            if not cloud_name:
                return Response({"error": "Cloudinary not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            url = f"https://api.cloudinary.com/v1_1/{cloud_name}/auto/upload"
            data = {
                "upload_preset": "fitna_uploads"
            }
            files = {
                "file": (file_obj.name, file_obj.read(), file_obj.content_type)
            }
            
            response = requests.post(url, data=data, files=files)
            response_data = response.json()
            
            if response.status_code == 200:
                return Response({"url": response_data.get("secure_url")})
            else:
                return Response({"error": response_data.get("error", {}).get("message", "Upload failed")}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from core.permissions import IsSuperAdmin, IsModuleAdmin

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['SUPER_ADMIN', 'MODULE_ADMIN'])

class SiteSettingsView(views.APIView):
    permission_classes = (IsAdminUser,)
    
    def get(self, request):
        from .models import SiteSettings
        from .serializers import SiteSettingsSerializer
        settings = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings)
        return Response(serializer.data)
        
    def post(self, request):
        if request.user.role != 'SUPER_ADMIN':
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
            
        action = request.data.get('action', 'update')
        if action == 'test_email':
            # Dummy test email success response since SMTP is not fully configured here
            return Response({"message": "تم إرسال بريد الاختبار بنجاح (Simulation)"})
            
        from .models import SiteSettings
        from .serializers import SiteSettingsSerializer
        settings = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class PublicSiteSettingsView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        from .models import SiteSettings
        from .serializers import SiteSettingsSerializer
        settings = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings)
        return Response(serializer.data)

class SuperAdminStatsView(views.APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        if request.user.role == 'SUPER_ADMIN':
            return Response({
                "total_users": User.objects.count(),
                "total_students": User.objects.filter(role='STUDENT').count(),
                "active_students": User.objects.filter(role='STUDENT', is_approved=True).count(),
                "pending_students": User.objects.filter(role='STUDENT', is_approved=False).count(),
                "total_module_admins": User.objects.filter(role='MODULE_ADMIN').count(),
                "total_modules": Module.objects.count(),
                "total_enrollments": Enrollment.objects.count()
            })
        else:
            my_modules = Module.objects.filter(admin=request.user)
            my_enrollments = Enrollment.objects.filter(module__in=my_modules)
            my_students = User.objects.filter(role='STUDENT', enrollments__in=my_enrollments).distinct()
            return Response({
                "total_users": my_students.count(),
                "total_students": my_students.count(),
                "active_students": my_students.filter(is_approved=True).count(),
                "pending_students": my_students.filter(is_approved=False).count(),
                "total_modules": my_modules.count(),
                "total_enrollments": my_enrollments.count()
            })

class SuperAdminUsersView(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.role == 'SUPER_ADMIN':
            return User.objects.all().order_by('-date_joined')
        else:
            # Module Admin can only see their students
            return User.objects.filter(
                role='STUDENT',
                enrollments__module__admin=self.request.user
            ).distinct().order_by('-date_joined')

class SuperAdminAssignModuleAdminView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request, slug):
        module = get_object_or_404(Module, slug=slug)
        user_id = request.data.get('user_id')
        
        user = get_object_or_404(User, id=user_id, role='MODULE_ADMIN')
        
        module.admin = user
        module.save()
        
        return Response({"message": f"Assigned {user.full_name} as admin for {module.name}"})

class SuperAdminAddStudentModuleView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request, pk):
        student = get_object_or_404(User, pk=pk, role='STUDENT')
        module_slug = request.data.get('module_slug')
        module = get_object_or_404(Module, slug=module_slug)
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            module=module,
            defaults={
                'is_primary': False,
                'enrolled_by': request.user
            }
        )
        
        if created:
            return Response({"message": f"Added {student.full_name} to {module.name}"})
        return Response({"message": "Student is already enrolled in this module"}, status=status.HTTP_400_BAD_REQUEST)

class SuperAdminModulesView(views.APIView):
    permission_classes = (IsAdminUser,)
    
    def get(self, request):
        if request.user.role == 'SUPER_ADMIN':
            modules = Module.objects.all().annotate(student_count=Count('enrollments'))
        else:
            modules = Module.objects.filter(admin=request.user).annotate(student_count=Count('enrollments'))
            
        data = []
        for m in modules:
            data.append({
                "slug": m.slug,
                "name": m.name,
                "admin": m.admin.full_name if m.admin else None,
                "student_count": m.student_count,
                "is_active": m.is_active
            })
        return Response(data)

class DashboardStatsView(views.APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        from django.db.models import Sum, Count, Q
        from django.utils import timezone
        import datetime
        
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Base queryset
        if request.user.role == 'SUPER_ADMIN':
            modules = Module.objects.all()
        else:
            modules = Module.objects.filter(admin=request.user)
            
        # Optimize with annotations instead of loop (Eliminates N+1)
        modules = modules.annotate(
            total_students_count=Count('enrollments', distinct=True),
            active_students_count=Count('enrollments', filter=Q(enrollments__student__is_approved=True), distinct=True),
            new_students_month_count=Count('enrollments', filter=Q(enrollments__enrolled_at__gte=start_of_month), distinct=True),
            revenue_sum=Sum('payments__amount', filter=Q(payments__payment_status='SUCCESS'))
        ).select_related('admin')

        data = []
        for m in modules:
            data.append({
                "slug": m.slug,
                "name": m.name,
                "admin": m.admin.full_name if m.admin else "No Admin",
                "total_students": m.total_students_count,
                "active_students": m.active_students_count,
                "new_students_month": m.new_students_month_count,
                "revenue": m.revenue_sum or 0,
                "completion_percent": 0 # simplified
            })
            
        return Response(data)

class StudentEnrollmentsView(views.APIView):
    permission_classes = (IsAdminUser,)
    
    def get(self, request, pk):
        enrollments = Enrollment.objects.filter(student_id=pk).select_related('module')
        data = []
        for e in enrollments:
            data.append({
                "id": e.id,
                "module_name": e.module.name,
                "enrolled_at": e.enrolled_at,
                "progress": 0, # Placeholder
                "status": "ACTIVE"
            })
        return Response(data)

class StudentPaymentsView(views.APIView):
    permission_classes = (IsAdminUser,)
    
    def get(self, request, pk):
        from modules.models import Payment
        payments = Payment.objects.filter(student_id=pk).select_related('module').order_by('-created_at')
        data = []
        for p in payments:
            data.append({
                "id": p.id,
                "module_name": p.module.name,
                "amount": p.amount,
                "method": p.payment_method,
                "status": p.payment_status,
                "created_at": p.created_at,
                "receipt_number": p.receipt_number,
                "admin": "System"
            })
        return Response(data)

class UsersExportView(views.APIView):
    permission_classes = (IsAdminUser,)
    
    def get(self, request):
        from django.http import HttpResponse
        import csv
        import openpyxl
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        role = request.GET.get('role', 'STUDENT')
        export_format = request.GET.get('format', 'csv')
        
        if request.user.role == 'SUPER_ADMIN':
            users = User.objects.filter(role=role).order_by('-date_joined')
        else:
            if role == 'STUDENT':
                users = User.objects.filter(role='STUDENT', enrollments__module__admin=request.user).distinct().order_by('-date_joined')
            else:
                return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
                
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="users_{role.lower()}_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ID', 'Full Name', 'Email', 'Phone', 'Status', 'Date Joined'])
            
            for u in users:
                writer.writerow([
                    u.id, 
                    u.full_name, 
                    u.email, 
                    u.phone_number, 
                    'Active' if u.is_active else 'Suspended',
                    u.date_joined.strftime("%Y-%m-%d %H:%M:%S")
                ])
            return response
            
        elif export_format == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="users_{role.lower()}_export.xlsx"'
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Users"
            ws.append(['ID', 'Full Name', 'Email', 'Phone', 'Status', 'Date Joined'])
            
            for u in users:
                ws.append([
                    u.id, 
                    u.full_name, 
                    u.email, 
                    str(u.phone_number), 
                    'Active' if u.is_active else 'Suspended',
                    u.date_joined.strftime("%Y-%m-%d %H:%M:%S")
                ])
            wb.save(response)
            return response
            
        elif export_format == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="users_{role.lower()}_export.pdf"'
            
            p = canvas.Canvas(response, pagesize=letter)
            p.drawString(100, 750, f"Users Export ({role})")
            y = 700
            for u in users[:50]: # limit to 50 for pdf simplicity
                p.drawString(100, y, f"ID: {u.id} | Name: {u.full_name} | Email: {u.email}")
                y -= 20
                if y < 50:
                    p.showPage()
                    y = 750
            p.showPage()
            p.save()
            return response

        return Response({"error": "Invalid format"}, status=400)

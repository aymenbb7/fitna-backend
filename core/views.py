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
            return Response({"message": "تم إرسال بريد الاختبار بنجاح (Simulation)"})
            
        from .models import SiteSettings
        from .serializers import SiteSettingsSerializer
        s = SiteSettings.load()
        
        # Safe text/scalar fields - never pass image fields through JSON to avoid validation errors
        text_fields = [
            'site_name', 'logo_url', 'site_primary_color', 'site_secondary_color',
            'landing_hero_title', 'landing_hero_subtitle', 'landing_hero_button_text', 'landing_hero_button_url',
            'landing_about_title', 'landing_about_text',
            'landing_programs_json', 'landing_features_json', 'landing_stats_json',
            'landing_testimonials_json', 'landing_faq_json',
            'landing_features_title', 'landing_features_subtitle', 'landing_stats_title',
            'landing_programs_title', 'landing_how_it_works_title', 'landing_testimonials_title',
            'landing_faq_title',
            'landing_cta_title', 'landing_cta_text', 'landing_cta_button_text', 'landing_cta_button_url',
            'contact_email', 'contact_phone', 'contact_address',
            'footer_text', 'footer_desc',
            'social_facebook', 'social_instagram', 'social_tiktok', 'social_whatsapp',
            'smtp_host', 'smtp_port', 'smtp_username', 'smtp_use_tls',
        ]
        for field in text_fields:
            if field in request.data:
                val = request.data[field]
                if field == 'smtp_port':
                    setattr(s, field, int(val) if val else 587)
                elif field == 'smtp_use_tls':
                    setattr(s, field, str(val).lower() == 'true')
                else:
                    setattr(s, field, val if val is not None else "")
        
        # File uploads only
        if 'logo' in request.FILES:
            s.logo = request.FILES['logo']
        if 'landing_hero_image' in request.FILES:
            s.landing_hero_image = request.FILES['landing_hero_image']
        if 'landing_about_image' in request.FILES:
            s.landing_about_image = request.FILES['landing_about_image']
        
        # Handle password separately
        pwd = request.data.get('smtp_password', '')
        if pwd and pwd != '********':
            s.smtp_password = pwd
            
        s.save()
        return Response({"message": "تم حفظ الإعدادات بنجاح"})

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

class SuperAdminCreateStudentView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request):
        from django.contrib.auth import get_user_model
        from modules.models import Module, Enrollment, Payment
        
        User = get_user_model()
        data = request.data
        
        email = data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({"error": "البريد الإلكتروني موجود مسبقاً"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            student = User.objects.create_user(
                username=email,
                email=email,
                password=data.get('password'),
                full_name=data.get('full_name'),
                phone_number=data.get('phone_number', ''),
                age=data.get('age'),
                role='STUDENT',
                is_approved=True
            )
            
            module_slugs = data.get('module_slugs', [])
            for slug in module_slugs:
                module = Module.objects.filter(slug=slug).first()
                if module:
                    Enrollment.objects.create(
                        student=student,
                        module=module,
                        is_primary=False,
                        enrolled_by=request.user
                    )
                    Payment.objects.create(
                        student=student,
                        module=module,
                        amount=module.price,
                        payment_method='CASH',
                        payment_status='SUCCESS',
                        created_by=request.user
                    )
                    
            from users.serializers import UserSerializer
            return Response(UserSerializer(student).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SuperAdminModuleUpdateView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request, slug):
        from modules.models import Module
        from django.contrib.auth import get_user_model
        User = get_user_model()
        module = get_object_or_404(Module, slug=slug)
        data = request.data
        
        # Text fields
        if 'name' in data:
            module.name = data['name']
        if 'description' in data:
            module.description = data['description']
        if 'price' in data:
            module.price = data['price']
        if 'learning_outcomes' in data:
            module.learning_outcomes = data['learning_outcomes']
        if 'benefits' in data:
            module.benefits = data['benefits']
        
        # Boolean handling since FormData sends strings 'true'/'false'
        if 'is_active' in data:
            val = data['is_active']
            if str(val).lower() == 'true':
                module.is_active = True
            elif str(val).lower() == 'false':
                module.is_active = False
            else:
                module.is_active = bool(val)
                
        # File uploads
        if 'thumbnail' in request.FILES:
            module.thumbnail = request.FILES['thumbnail']
        if 'hero_image' in request.FILES:
            module.hero_image = request.FILES['hero_image']
            
        # Admin assignment
        admin_id = data.get('admin_id')
        if admin_id:
            try:
                admin_user = User.objects.get(id=admin_id, role='MODULE_ADMIN')
                module.admin = admin_user
            except User.DoesNotExist:
                pass
                
        module.save()
        return Response({"message": f"Module {module.name} updated successfully."})

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
        
        role = request.GET.get('role', 'STUDENT')
        export_format = request.GET.get('export_format', 'csv')
        
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
            import os
            from django.conf import settings
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.pdfbase import pdfmetrics
            import arabic_reshaper
            from bidi.algorithm import get_display

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="users_{role.lower()}_export.pdf"'
            
            font_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'fonts', 'Amiri-Regular.ttf')
            pdfmetrics.registerFont(TTFont('Arabic', font_path))

            def render_arabic(text):
                if not text:
                    return ''
                return get_display(arabic_reshaper.reshape(str(text)))

            doc = SimpleDocTemplate(response, pagesize=landscape(letter))
            elements = []

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(name='TitleStyle', fontName='Arabic', fontSize=18, alignment=1)
            elements.append(Paragraph(render_arabic(f'تقرير المستخدمين - منصة فطنة ({role})'), title_style))
            elements.append(Spacer(1, 20))

            data = [[
                render_arabic('تاريخ الانضمام'), 
                render_arabic('الحالة'), 
                render_arabic('رقم الهاتف'), 
                render_arabic('البريد الإلكتروني'), 
                render_arabic('الاسم الكامل'), 
                render_arabic('ID')
            ]]

            for u in users:
                data.append([
                    u.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                    render_arabic('نشط' if u.is_active else 'موقوف'),
                    str(u.phone_number),
                    u.email,
                    render_arabic(u.full_name),
                    str(u.id)
                ])

            table = Table(data, colWidths=[100, 60, 100, 150, 150, 40])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D0B2B')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), 'Arabic'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f9f9f9')),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cccccc')),
            ]))

            elements.append(table)
            doc.build(elements)
            return response

        return Response({"error": "Invalid format"}, status=400)

class SuperAdminUserUpdateView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request, pk):
        from django.contrib.auth import get_user_model
        from modules.models import Module
        User = get_user_model()
        user = get_object_or_404(User, pk=pk)
        
        data = request.data
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            user.email = data['email']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'username' in data:
            user.username = data['username']
            
        user.save()
        
        if user.role == 'MODULE_ADMIN' and 'module_slugs' in data:
            # Unassign all modules
            Module.objects.filter(admin=user).update(admin=None)
            # Reassign new ones
            for slug in data['module_slugs']:
                module = Module.objects.filter(slug=slug).first()
                if module:
                    module.admin = user
                    module.save()
                    
        if user.role == 'STUDENT' and 'module_slugs' in data:
            from modules.models import Enrollment
            new_slugs = set(data['module_slugs'])
            current_enrollments = Enrollment.objects.filter(student=user)
            current_slugs = set(current_enrollments.values_list('module__slug', flat=True))
            
            # Remove unselected
            to_remove = current_slugs - new_slugs
            if to_remove:
                Enrollment.objects.filter(student=user, module__slug__in=to_remove).delete()
            
            # Add new selected
            to_add = new_slugs - current_slugs
            for slug in to_add:
                module = Module.objects.filter(slug=slug).first()
                if module:
                    Enrollment.objects.get_or_create(student=user, module=module)
                    
        return Response({"message": "User updated successfully"})

class SuperAdminUserStatusView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request, pk):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = get_object_or_404(User, pk=pk)
        if 'is_active' in request.data:
            user.is_active = request.data['is_active']
            user.save()
        return Response({"message": "Status updated successfully"})

class SuperAdminUserResetPasswordView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request, pk):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = get_object_or_404(User, pk=pk)
        if 'password' in request.data:
            user.set_password(request.data['password'])
            user.save()
        return Response({"message": "Password reset successfully"})

class SuperAdminCreateModuleAdminView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request):
        from django.contrib.auth import get_user_model
        from modules.models import Module
        User = get_user_model()
        data = request.data
        email = data.get('email')
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            admin_user = User.objects.create_user(
                email=email,
                password=data.get('password'),
                full_name=data.get('full_name'),
                phone_number=data.get('phone_number', ''),
                username=data.get('username', ''),
                role='MODULE_ADMIN',
                is_approved=True
            )
            
            module_slugs = data.get('module_slugs', [])
            for slug in module_slugs:
                module = Module.objects.filter(slug=slug).first()
                if module:
                    module.admin = admin_user
                    module.save()
                    
            from users.serializers import UserSerializer
            return Response(UserSerializer(admin_user).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SuperAdminModuleStatsView(views.APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request, slug):
        from modules.models import Module, Enrollment
        from django.db.models import Sum
        
        module = get_object_or_404(Module, slug=slug)
        
        if request.user.role == 'MODULE_ADMIN' and module.admin != request.user:
            return Response({'error': 'Unauthorized'}, status=403)
            
        enrollments = Enrollment.objects.filter(module=module)
        total_students = enrollments.count()
        
        from modules.models import Payment
        payments = Payment.objects.filter(module=module, payment_status='SUCCESS')
        total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        latest_payments = payments.order_by('-created_at')[:5]
        latest_payments_data = [{
            'student_name': p.student.full_name,
            'amount': p.amount,
            'method': p.payment_method,
            'paid_at': p.created_at
        } for p in latest_payments]
        
        return Response({
            'price': module.price,
            'total_students': total_students,
            'total_revenue': total_revenue,
            'average_revenue': total_revenue / total_students if total_students > 0 else 0,
            'latest_payments': latest_payments_data
        })

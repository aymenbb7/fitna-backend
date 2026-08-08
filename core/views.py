from rest_framework import permissions
import cloudinary.uploader
from rest_framework import views, status, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSuperAdmin, IsModuleAdmin
from django.contrib.auth import get_user_model
from modules.models import Module, Enrollment, Payment
from users.serializers import UserSerializer
from django.db.models import Count, Sum, Q
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import transaction
from django.utils import timezone
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
            import cloudinary
            import cloudinary.uploader

            # Configure cloudinary with credentials from Django settings
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
                api_key=settings.CLOUDINARY_STORAGE.get('API_KEY'),
                api_secret=settings.CLOUDINARY_STORAGE.get('API_SECRET'),
                secure=True,
            )

            if not settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'):
                return Response({"error": "Cloudinary not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Determine resource type from MIME
            content_type = file_obj.content_type or ''
            if content_type.startswith('image/'):
                resource_type = 'image'
            elif content_type.startswith('video/') or content_type.startswith('audio/'):
                resource_type = 'video'
            else:
                resource_type = 'raw'

            result = cloudinary.uploader.upload(
                file_obj,
                resource_type=resource_type,
                folder='fitna_uploads',
                use_filename=True,
                unique_filename=True,
            )

            secure_url = result.get('secure_url')
            if secure_url:
                return Response({"url": secure_url})
            else:
                return Response({"error": "Upload succeeded but no URL returned"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['SUPER_ADMIN', 'MODULE_ADMIN'])


class SiteSettingsView(views.APIView):
    permission_classes = (IsAdminUser,)
    
    def get(self, request):
        from .models import SiteSettings
        from .serializers import SiteSettingsSerializer
        settings_obj = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings_obj)
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

        model_field_names = {f.name for f in SiteSettings._meta.get_fields()}
        allowed_fields = model_field_names - {'id'}

        for field in allowed_fields:
            if field in request.data:
                val = request.data[field]
                if field == 'smtp_port':
                    try:
                        setattr(s, field, int(val) if (val != '' and val is not None) else 587)
                    except (ValueError, TypeError):
                        setattr(s, field, 587)
                elif field == 'smtp_use_tls':
                    setattr(s, field, str(val).lower() in ('true', '1', 'yes'))
                elif field in ['logo', 'landing_hero_image', 'landing_about_image']:
                    if val is None or val == '':
                        continue
                    else:
                        setattr(s, field, val)
                else:
                    setattr(s, field, val if val is not None else '')

        pwd = request.data.get('smtp_password', '')
        if pwd and pwd != '********':
            s.smtp_password_encrypted = pwd

        try:
            s.full_clean()
            s.save()
        except Exception as e:
            # Handle Django ValidationError and format it
            from django.core.exceptions import ValidationError
            if isinstance(e, ValidationError):
                error_dict = getattr(e, 'message_dict', {})
                if error_dict:
                    # Return the first error message
                    first_field = list(error_dict.keys())[0]
                    first_error = error_dict[first_field][0]
                    return Response({"error": f"{first_field}: {first_error}"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SiteSettingsSerializer(s)
        return Response({"message": "تم حفظ الإعدادات بنجاح", "settings": serializer.data})


class PublicSiteSettingsView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        from .models import SiteSettings
        from .serializers import SiteSettingsSerializer
        settings_obj = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings_obj)
        return Response(serializer.data)


class SuperAdminStatsView(views.APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        if request.user.role == 'SUPER_ADMIN':
            return Response({
                "total_users": User.objects.count(),
                "total_students": User.objects.filter(role='STUDENT').count(),
                "active_students": User.objects.filter(role='STUDENT', is_approved=True, is_active=True).count(),
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
                "active_students": my_students.filter(is_approved=True, is_active=True).count(),
                "pending_students": my_students.filter(is_approved=False).count(),
                "total_modules": my_modules.count(),
                "total_enrollments": my_enrollments.count()
            })


class SuperAdminUsersView(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = User.objects.all()
        if self.request.user.role != 'SUPER_ADMIN':
            qs = qs.filter(role='STUDENT', enrollments__module__admin=self.request.user).distinct()
            
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(full_name__icontains=search) | Q(email__icontains=search) | Q(phone_number__icontains=search))
            
        return qs.prefetch_related('enrollments__module', 'notifications', 'payments__module').order_by('-date_joined')


class SuperAdminUserDeleteView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({"message": "تم حذف المستخدم بنجاح"})

    def post(self, request, pk):
        return self.delete(request, pk)


class SuperAdminCreateStudentView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request):
        data = request.data
        email = data.get('email')
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "البريد الإلكتروني موجود مسبقاً"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic():
                student = User.objects.create_user(
                    username=email,
                    email=email,
                    password=data.get('password'),
                    full_name=data.get('full_name'),
                    phone_number=data.get('phone_number', ''),
                    age=data.get('age'),
                    role='STUDENT',
                    is_active=True,
                    is_approved=True
                )
                
                module_slugs = data.get('module_slugs', [])
                payments_data = data.get('payments', [])
                payments_dict = {p.get('module_slug'): p for p in payments_data if isinstance(p, dict)}

                for slug in module_slugs:
                    module = Module.objects.filter(slug=slug).first()
                    if module:
                        Enrollment.objects.get_or_create(
                            student=student,
                            module=module,
                            defaults={
                                'is_primary': False,
                                'enrolled_by': request.user
                            }
                        )
                        pay_info = payments_dict.get(slug, {})
                        payment_method = pay_info.get('method', 'CASH')
                        receipt_num = pay_info.get('receipt_number') or None
                        
                        Payment.objects.create(
                            student=student,
                            module=module,
                            amount=module.price,
                            payment_method=payment_method,
                            payment_status='SUCCESS',
                            receipt_number=receipt_num,
                            paid_at=timezone.now()
                        )
                        
            return Response({"message": "تم إنشاء حساب الطالب بنجاح", "student": UserSerializer(student).data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ModuleAdminCreateStudentView(views.APIView):
    """Allows MODULE_ADMIN to create a student and enroll them in their own modules only."""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.user.role not in ['SUPER_ADMIN', 'MODULE_ADMIN']:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        email = data.get('email')

        if User.objects.filter(email=email).exists():
            return Response({"error": "البريد الإلكتروني موجود مسبقاً"}, status=status.HTTP_400_BAD_REQUEST)

        # For module admin: only allow enrolling in their own modules
        if request.user.role == 'MODULE_ADMIN':
            my_module_slugs = list(Module.objects.filter(admin=request.user).values_list('slug', flat=True))
            requested_slugs = data.get('module_slugs', [])
            # Silently restrict to only their modules
            allowed_slugs = [s for s in requested_slugs if s in my_module_slugs]
        else:
            allowed_slugs = data.get('module_slugs', [])

        try:
            with transaction.atomic():
                student = User.objects.create_user(
                    username=email,
                    email=email,
                    password=data.get('password'),
                    full_name=data.get('full_name'),
                    phone_number=data.get('phone_number', ''),
                    age=data.get('age'),
                    role='STUDENT',
                    is_active=True,
                    is_approved=True
                )

                payments_data = data.get('payments', [])
                payments_dict = {p.get('module_slug'): p for p in payments_data if isinstance(p, dict)}

                for slug in allowed_slugs:
                    module = Module.objects.filter(slug=slug).first()
                    if module:
                        Enrollment.objects.get_or_create(
                            student=student,
                            module=module,
                            defaults={
                                'is_primary': False,
                                'enrolled_by': request.user
                            }
                        )
                        pay_info = payments_dict.get(slug, {})
                        payment_method = pay_info.get('method', 'CASH')
                        receipt_num = pay_info.get('receipt_number') or None

                        Payment.objects.create(
                            student=student,
                            module=module,
                            amount=module.price,
                            payment_method=payment_method,
                            payment_status='SUCCESS',
                            receipt_number=receipt_num,
                            paid_at=timezone.now()
                        )

            return Response({"message": "تم إنشاء حساب الطالب بنجاح", "student": UserSerializer(student).data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SuperAdminModuleUpdateView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def has_module_permission(self, request, module):
        """Returns True if the user is allowed to update this module."""
        user = request.user
        if user.role == 'SUPER_ADMIN':
            return True
        if user.role == 'MODULE_ADMIN':
            try:
                return user.managed_module.slug == module.slug
            except Exception:
                return False
        return False

    def post(self, request, slug):
        module = get_object_or_404(Module, slug=slug)
        if not self.has_module_permission(request, module):
            return Response({"detail": "You do not have permission to perform this action."}, status=403)

        data = request.data
        is_super = request.user.role == 'SUPER_ADMIN'

        # Fields available to all admins (MODULE_ADMIN + SUPER_ADMIN)
        if 'name' in data:
            module.name = data['name']
        if 'description' in data:
            module.description = data['description']
        if 'learning_outcomes' in data:
            module.learning_outcomes = data['learning_outcomes']
        if 'benefits' in data:
            module.benefits = data['benefits']
        if 'thumbnail' in data and data['thumbnail']:
            module.cover_image_url = data['thumbnail']
        if 'thumbnail' in request.FILES:
            module.thumbnail = request.FILES['thumbnail']
        if 'hero_image' in request.FILES:
            module.hero_image = request.FILES['hero_image']

        # Fields restricted to SUPER_ADMIN only
        if is_super:
            if 'price' in data:
                module.price = data['price']
            if 'is_active' in data:
                val = data['is_active']
                if str(val).lower() == 'true':
                    module.is_active = True
                elif str(val).lower() == 'false':
                    module.is_active = False
                else:
                    module.is_active = bool(val)
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
            Payment.objects.create(
                student=student,
                module=module,
                amount=module.price,
                payment_method='CASH',
                payment_status='SUCCESS',
                paid_at=timezone.now()
            )
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
                "id": m.id,
                "slug": m.slug,
                "name": m.name,
                "price": float(m.price) if m.price is not None else 0,
                "admin": m.admin.full_name if m.admin else None,
                "student_count": m.student_count,
                "is_active": m.is_active
            })
        return Response(data)


class DashboardStatsView(views.APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if request.user.role == 'SUPER_ADMIN':
            modules = Module.objects.all()
        else:
            modules = Module.objects.filter(admin=request.user)
            
        modules = modules.annotate(
            total_students_count=Count('enrollments', distinct=True),
            active_students_count=Count('enrollments', filter=Q(enrollments__student__is_approved=True), distinct=True),
            new_students_month_count=Count('enrollments', filter=Q(enrollments__enrolled_at__gte=start_of_month), distinct=True),
            revenue_sum=Sum('payments__amount', filter=Q(payments__payment_status='SUCCESS'))
        ).select_related('admin')

        data = []
        for m in modules:
            rev = float(m.revenue_sum or 0)
            if rev == 0 and m.total_students_count > 0:
                rev = float(m.total_students_count * m.price)
                
            data.append({
                "slug": m.slug,
                "name": m.name,
                "admin": m.admin.full_name if m.admin else "No Admin",
                "total_students": m.total_students_count,
                "active_students": m.active_students_count,
                "new_students_month": m.new_students_month_count,
                "revenue": rev,
                "completion_percent": 0
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
                "module_name": e.module.name if e.module else '',
                "enrolled_at": e.enrolled_at,
                "progress": 0,
                "status": "ACTIVE"
            })
        return Response(data)


class StudentPaymentsView(views.APIView):
    permission_classes = (IsAdminUser,)
    
    def get(self, request, pk):
        payments = Payment.objects.filter(student_id=pk).select_related('module').order_by('-created_at')
        data = []
        for p in payments:
            data.append({
                "id": p.id,
                "module_name": p.module.name if p.module else '',
                "amount": float(p.amount),
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
                    str(u.phone_number or ''), 
                    'Active' if u.is_active else 'Suspended',
                    u.date_joined.strftime("%Y-%m-%d %H:%M:%S")
                ])
            wb.save(response)
            return response
            
        elif export_format == 'pdf':
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from core.pdf_utils import setup_arabic_font, render_arabic

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="users_{role.lower()}_export.pdf"'
            
            font_name = setup_arabic_font()

            doc = SimpleDocTemplate(response, pagesize=landscape(letter))
            elements = []

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(name='TitleStyle', fontName=font_name, fontSize=18, alignment=1)
            elements.append(Paragraph(render_arabic(f'تقرير المستخدمين - منصة فطنة ({role})', font_name), title_style))
            elements.append(Spacer(1, 20))

            data = [[
                render_arabic('تاريخ الانضمام', font_name), 
                render_arabic('الحالة', font_name), 
                render_arabic('رقم الهاتف', font_name), 
                render_arabic('البريد الإلكتروني', font_name), 
                render_arabic('الاسم الكامل', font_name), 
                render_arabic('ID', font_name)
            ]]

            for u in users:
                data.append([
                    u.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                    render_arabic('نشط' if u.is_active else 'موقوف', font_name),
                    str(u.phone_number or ''),
                    u.email or '',
                    render_arabic(u.full_name or '', font_name),
                    str(u.id)
                ])

            table = Table(data, colWidths=[100, 60, 100, 150, 150, 40])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D0B2B')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), font_name),
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
        if 'is_approved' in data:
            val = data['is_approved']
            user.is_approved = str(val).lower() in ('true', '1', 'yes') if isinstance(val, str) else bool(val)
            if user.is_approved:
                user.is_active = True
        if 'is_active' in data:
            val = data['is_active']
            user.is_active = str(val).lower() in ('true', '1', 'yes') if isinstance(val, str) else bool(val)
            
        user.save()
        
        if user.role == 'MODULE_ADMIN' and 'module_slugs' in data:
            Module.objects.filter(admin=user).update(admin=None)
            for slug in data['module_slugs']:
                module = Module.objects.filter(slug=slug).first()
                if module:
                    module.admin = user
                    module.save()
                    
        if user.role == 'STUDENT' and 'module_slugs' in data:
            new_slugs = set(data['module_slugs'])
            current_enrollments = Enrollment.objects.filter(student=user)
            current_slugs = set(current_enrollments.values_list('module__slug', flat=True))
            
            to_remove = current_slugs - new_slugs
            if to_remove:
                Enrollment.objects.filter(student=user, module__slug__in=to_remove).delete()
            
            to_add = new_slugs - current_slugs
            for slug in to_add:
                module = Module.objects.filter(slug=slug).first()
                if module:
                    Enrollment.objects.get_or_create(student=user, module=module)
                    Payment.objects.get_or_create(
                        student=user,
                        module=module,
                        defaults={
                            'amount': module.price,
                            'payment_method': 'CASH',
                            'payment_status': 'SUCCESS',
                            'paid_at': timezone.now()
                        }
                    )
                    
        return Response({"message": "User updated successfully"})


class SuperAdminUserStatusView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if 'is_active' in request.data:
            val = request.data['is_active']
            user.is_active = str(val).lower() in ('true', '1', 'yes') if isinstance(val, str) else bool(val)
            user.save()
        return Response({"message": "Status updated successfully"})


class SuperAdminUserResetPasswordView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if 'password' in request.data:
            user.set_password(request.data['password'])
            user.save()
        return Response({"message": "Password reset successfully"})


class SuperAdminCreateModuleAdminView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def post(self, request):
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
                is_active=True,
                is_approved=True
            )
            
            module_slugs = data.get('module_slugs', [])
            for slug in module_slugs:
                module = Module.objects.filter(slug=slug).first()
                if module:
                    module.admin = admin_user
                    module.save()
                    
            return Response(UserSerializer(admin_user).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SuperAdminModuleStatsView(views.APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request, slug):
        module = get_object_or_404(Module, slug=slug)
        
        if request.user.role == 'MODULE_ADMIN' and module.admin != request.user:
            return Response({'error': 'Unauthorized'}, status=403)
            
        enrollments = Enrollment.objects.filter(module=module)
        total_students = enrollments.count()
        
        payments = Payment.objects.filter(module=module, payment_status='SUCCESS')
        payment_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        if payment_revenue == 0 and total_students > 0:
            total_revenue = float(total_students * module.price)
        else:
            total_revenue = float(payment_revenue)
            
        average_revenue = total_revenue / total_students if total_students > 0 else 0
        
        latest_payments = payments.order_by('-created_at')[:5]
        latest_payments_data = []
        for p in latest_payments:
            latest_payments_data.append({
                'student_name': p.student.full_name or p.student.email if p.student else '',
                'amount': float(p.amount),
                'method': p.payment_method,
                'paid_at': p.paid_at or p.created_at
            })
            
        if not latest_payments_data and total_students > 0:
            for e in enrollments.select_related('student').order_by('-enrolled_at')[:5]:
                latest_payments_data.append({
                    'student_name': e.student.full_name or e.student.email if e.student else '',
                    'amount': float(module.price),
                    'method': 'CASH',
                    'paid_at': e.enrolled_at
                })

        return Response({
            'price': float(module.price),
            'total_students': total_students,
            'total_revenue': total_revenue,
            'average_revenue': average_revenue,
            'latest_payments': latest_payments_data
        })

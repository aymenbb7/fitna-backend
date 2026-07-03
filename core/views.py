import cloudinary.uploader
from rest_framework import views, status, generics
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

class SuperAdminStatsView(views.APIView):
    permission_classes = (IsSuperAdmin,)

    def get(self, request):
        total_users = User.objects.count()
        total_students = User.objects.filter(role='STUDENT').count()
        active_students = User.objects.filter(role='STUDENT', is_approved=True).count()
        pending_students = User.objects.filter(role='STUDENT', is_approved=False).count()
        total_modules = Module.objects.count()
        total_enrollments = Enrollment.objects.count()

        return Response({
            "total_users": total_users,
            "total_students": total_students,
            "active_students": active_students,
            "pending_students": pending_students,
            "total_modules": total_modules,
            "total_enrollments": total_enrollments
        })

class SuperAdminUsersView(generics.ListAPIView):
    permission_classes = (IsSuperAdmin,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

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
    permission_classes = (IsSuperAdmin,)
    
    def get(self, request):
        modules = Module.objects.all().annotate(student_count=Count('enrollments'))
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

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from modules.models import Module, Enrollment
from users.models import Notification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    enrolled_modules = serializers.SerializerMethodField()
    unread_notifications_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    purchase_history = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'role', 'is_approved', 'is_active', 'profile_picture', 'phone_number', 'age', 'enrolled_modules', 'unread_notifications_count', 'total_spent', 'purchase_history', 'last_login', 'date_joined')

    def get_enrolled_modules(self, obj):
        if obj.role != 'STUDENT':
            return []
        try:
            enrollments = [e for e in obj.enrollments.all() if e.module and e.module.is_active]
        except Exception:
            enrollments = Enrollment.objects.filter(student=obj, module__is_active=True).select_related('module')
            
        return [{
            "slug": e.module.slug,
            "name": e.module.name,
            "icon": e.module.icon,
            "color_primary": e.module.color_primary
        } for e in enrollments]

    def get_unread_notifications_count(self, obj):
        try:
            return sum(1 for n in obj.notifications.all() if not n.is_read)
        except Exception:
            return Notification.objects.filter(recipient=obj, is_read=False).count()
        
    def get_total_spent(self, obj):
        if obj.role != 'STUDENT':
            return 0
        try:
            return float(sum(p.amount for p in obj.payments.all() if p.payment_status == 'SUCCESS'))
        except Exception:
            from modules.models import Payment
            from django.db.models import Sum
            return float(Payment.objects.filter(student=obj, payment_status='SUCCESS').aggregate(Sum('amount'))['amount__sum'] or 0)

    def get_purchase_history(self, obj):
        if obj.role != 'STUDENT':
            return []
        try:
            payments = [p for p in obj.payments.all() if p.payment_status == 'SUCCESS']
        except Exception:
            from modules.models import Payment
            payments = Payment.objects.filter(student=obj, payment_status='SUCCESS').order_by('-created_at')
            
        return [{
            "id": p.id,
            "module": p.module.name if p.module else '',
            "amount": float(p.amount),
            "status": p.payment_status,
            "date": p.paid_at or p.created_at
        } for p in payments]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    module_slug = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name', 'phone_number', 'age', 'module_slug')

    def validate_age(self, value):
        if value is not None and not (9 <= value <= 18):
            raise serializers.ValidationError("Age must be between 9 and 18.")
        return value

    def create(self, validated_data):
        module_slug = validated_data.pop('module_slug')
        password = validated_data.pop('password')
        
        try:
            module = Module.objects.get(slug=module_slug, is_active=True)
        except Module.DoesNotExist:
            raise serializers.ValidationError({"module_slug": "Module does not exist or is inactive."})

        user = User.objects.create_user(
            username=validated_data.get('email'),
            password=password,
            **validated_data
        )

        Enrollment.objects.create(student=user, module=module, is_primary=True)

        if module.admin:
            Notification.objects.create(
                recipient=module.admin,
                title="New Student Registration",
                message=f"{user.full_name} has registered for {module.name} and is waiting for approval.",
                notification_type="NEW_STUDENT",
                related_module=module
            )

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        if self.user.role == 'STUDENT' and not self.user.is_approved:
            raise serializers.ValidationError({"detail": "Account is pending approval."})
            
        data['role'] = self.user.role
        data['full_name'] = self.user.full_name
        
        if self.user.role == 'STUDENT':
            enrollments = Enrollment.objects.filter(student=self.user, module__is_active=True)
            data['enrolled_modules'] = [{
                "slug": e.module.slug,
                "name": e.module.name,
                "icon": e.module.icon,
                "color_primary": e.module.color_primary
            } for e in enrollments]
        else:
            data['enrolled_modules'] = []

        return data

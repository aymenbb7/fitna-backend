from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'SUPER_ADMIN')

class IsModuleAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'MODULE_ADMIN')

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'STUDENT')

class IsEnrolledStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.role == 'STUDENT'):
            return False
        if not request.user.is_approved:
            return False
        
        module_slug = view.kwargs.get('slug')
        if not module_slug:
            return False
            
        return request.user.enrollments.filter(module__slug=module_slug).exists()

class IsModuleOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.role == 'MODULE_ADMIN'):
            return False
            
        module_slug = view.kwargs.get('slug')
        if not module_slug:
            return False
            
        return getattr(request.user, 'managed_module', None) is not None and request.user.managed_module.slug == module_slug

from rest_framework.permissions import BasePermission

from .models import Company


class IsAdminUser(BasePermission):
    message = "Admin access is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        company = getattr(request.user, "company", None)
        return bool(
            company
            and company.role == Company.Role.ADMIN
        )

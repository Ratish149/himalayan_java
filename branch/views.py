from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters
from rest_framework import generics, permissions

from .models import Branch
from .serializers import BranchSerializer


# -------------------------------
# Inline custom permission class
# -------------------------------
class IsSuperAdminOrBranchAdmin(permissions.BasePermission):
    """
    - Superadmin: full access
    - Admin: access only to their assigned branches
    - Staff: read-only (optional)
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Superadmin: unrestricted
        if user.role == "superadmin":
            return True

        # Admin: full CRUD on their branches
        if user.role == "admin":
            return True

        # Staff: read-only
        if user.role == "staff" and request.method in permissions.SAFE_METHODS:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Superadmin: unrestricted
        if user.role == "superadmin":
            return True

        # Admin: only on their assigned branches
        if user.role == "admin":
            return obj in user.branches.all()

        # Staff: read-only
        if user.role == "staff" and request.method in permissions.SAFE_METHODS:
            return True

        return False


# -------------------------------
# Branch Views
# -------------------------------
class BranchListCreateView(generics.ListCreateAPIView):
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrBranchAdmin]
    filter_backends = [DjangoFilterBackend, rest_filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return Branch.objects.all()


class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrBranchAdmin]
    queryset = Branch.objects.all()

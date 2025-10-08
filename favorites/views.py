from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import Favorite
from .serializers import FavoriteSerializer


# -----------------------
# Custom Permissions
# -----------------------
class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


class IsBranchAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


# -----------------------
# Favorite Views
# -----------------------
class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]  # can add custom roles if needed

    def get_queryset(self):
        user = self.request.user

        # If superadmin → can see all favorites
        if user.role == 'superadmin':
            return Favorite.objects.all()

        # If branch admin → can see all favorites in their branch
        if user.role == 'admin':
            return Favorite.objects.filter(branch=user.branch)

        # Regular user → only their own favorites
        return Favorite.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user

        if user.role == 'superadmin':
            return Favorite.objects.all()
        elif user.role == 'admin':
            return Favorite.objects.filter(branch=user.branch)
        else:
            return Favorite.objects.filter(user=user)

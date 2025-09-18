from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated

from .models import Redeem, UserRedeem
from .serializers import RedeemSerializer, UserRedeemSerializer, UserRedeemReadSerializer


class RedeemPointsView(generics.ListAPIView):
    """
    Public endpoint: View available redeem offers.
    """
    queryset = Redeem.objects.select_related('sub_category__category').all()
    serializer_class = RedeemSerializer


class UserRedeemView(generics.ListCreateAPIView):
    """
    Authenticated endpoint: View or create user's redemptions.
    """
    serializer_class = UserRedeemSerializer
    # Remove token requirement for this view; enforce auth only when necessary
    permission_classes = []

    def get_queryset(self):
        base_qs = UserRedeem.objects.select_related('user', 'redeem__sub_category__category')
        # If unauthenticated, return empty queryset to avoid leaking user data
        if not self.request.user or not self.request.user.is_authenticated:
            return base_qs.none()
        if getattr(self.request.user, 'is_staff', False):
            return base_qs
        return base_qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        if not self.request.user or not self.request.user.is_authenticated:
            raise NotAuthenticated("Authentication required to redeem points.")
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserRedeemReadSerializer
        return UserRedeemSerializer

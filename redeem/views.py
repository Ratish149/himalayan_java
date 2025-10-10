from rest_framework import generics
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated

from .models import Redeem, UserRedeem
from .serializers import (
    RedeemSerializer,
    UserRedeemPointsSerializer,
    UserRedeemReadSerializer,
    UserRedeemSerializer,
)


class RedeemPointsView(generics.ListCreateAPIView):
    """
    Public endpoint: View available redeem offers.
    """

    queryset = Redeem.objects.select_related("sub_category__category").all()
    serializer_class = RedeemSerializer


class RedeemPointsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all()


class UserRedeemView(generics.ListCreateAPIView):
    """
    Authenticated endpoint: View or create user's redemptions.
    """

    serializer_class = UserRedeemSerializer

    def get_queryset(self):
        base_qs = UserRedeem.objects.select_related(
            "user", "redeem__sub_category__category"
        )

        user = self.request.user
        if not user or not user.is_authenticated:
            # Prevent unauthorized access
            return base_qs.none()

        if user.is_staff:
            return base_qs  # Admin can view all
        return base_qs.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user or not user.is_authenticated:
            raise NotAuthenticated("Authentication required to redeem points.")
        serializer.save(user=user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserRedeemReadSerializer
        return UserRedeemSerializer


class UserRedeemNextOfferView(generics.RetrieveAPIView):
    """
    Authenticated endpoint: View user's redeem points summary with next coming offer.
    Returns the next offer that requires more points than the user currently has.
    """

    serializer_class = UserRedeemPointsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        user_points = getattr(user, "redeem_points", 0)  # Safe fallback

        # Find next affordable offer
        affordable_offers = (
            Redeem.objects.filter(redeem_points__gt=user_points)
            .select_related("sub_category__category")
            .order_by("redeem_points")
        )

        next_offer = affordable_offers.first() if affordable_offers.exists() else None

        return {
            "user_points": user_points,
            "next_offer": next_offer,
        }

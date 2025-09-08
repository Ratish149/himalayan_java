from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Redeem, UserRedeem
from .serializers import RedeemSerializer, UserRedeemSerializer


class RedeemPointsView(generics.ListAPIView):
    """
    Public endpoint: View available redeem offers.
    """
    queryset = Redeem.objects.all()
    serializer_class = RedeemSerializer


class UserRedeemView(generics.ListCreateAPIView):
    """
    Authenticated endpoint: View or create user's redemptions.
    """
    serializer_class = UserRedeemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserRedeem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

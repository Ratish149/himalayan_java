from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserRedeem, Redeem
from .serializers import (
    UserRedeemSerializer, 
    RedeemSerializer,
)

# Create your views here.
class RedeemPointsView(generics.ListCreateAPIView):
    queryset = Redeem.objects.all()
    serializer_class = RedeemSerializer
    # permission_classes = [IsAuthenticated]  # Fixed typo: was 'permission'


class UserRedeemView(generics.ListCreateAPIView):
    queryset = UserRedeem.objects.all()
    serializer_class = UserRedeemSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


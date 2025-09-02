from django.shortcuts import render
from rest_framework import generics
from .models import Favorite
from .serializers import FavoriteSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class FavoriteListView(generics.RetrieveDestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

class FavoriteDetailView(generics.RetrieveDestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

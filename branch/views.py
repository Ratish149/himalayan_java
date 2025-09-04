from django.shortcuts import render
from rest_framework import generics
from .models import Branch
from .serializers import BranchSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters

# Create your views here.


class BranchListCreateView(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.SearchFilter]
    search_fields = ['name']


class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    
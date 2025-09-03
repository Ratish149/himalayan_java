from django.urls import path
from .views import BranchListCreateView, BranchDetailView

urlpatterns = [
    path('branches/', BranchListCreateView.as_view(), name='branch-list'),
    path('branches/<int:pk>/', BranchDetailView.as_view(), name='branch-detail'),
]

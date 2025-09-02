from django.urls import path
from . import views

urlpatterns = [
    path('favorites/', views.FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/<int:pk>/', views.FavoriteDetailView.as_view(), name='favorite-detail'),
]

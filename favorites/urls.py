from django.urls import path
from .views import FavoriteListCreateView, FavoriteDetailView

urlpatterns = [
    path("favorites/", FavoriteListCreateView.as_view(), name="favorite-list-create"),
    path("favorites/<int:pk>/", FavoriteDetailView.as_view(), name="favorite-detail"),
]

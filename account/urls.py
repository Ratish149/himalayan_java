from django.urls import path
from . import views

urlpatterns=[
    path('register/',views.CustomUserList.as_view(),name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('profile/',views.ProfileView.as_view(),name='profile'),
]
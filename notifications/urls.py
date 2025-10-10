from django.urls import path

from . import views

urlpatterns = [
    path("test-notifications/", views.test_notifications, name="test_notifications"),
    path(
        "send-notification/",
        views.SendNotificationAPIView.as_view(),
        name="send-notification-api",
    ),
]

from django.urls import path

from . import views

urlpatterns = [
    path("test-notifications/", views.test_notifications, name="test_notifications"),
    path(
        "send-notification/",
        views.SendNotificationAPIView.as_view(),
        name="send-notification-api",
    ),
    path(
        "notifications/",
        views.NotificationListAPIView.as_view(),
        name="notification-list-api",
    ),
    path(
        "notification/<int:pk>/",
        views.NotificationRetrieveUpdateDestroyAPIView.as_view(),
        name="notification-detail-api",
    ),
    path(
        "register-device/",
        views.RegisterDeviceAPIView.as_view(),
        name="register-device-api",
    ),
    path("test-push/", views.test_push_notification, name="test-push"),
]

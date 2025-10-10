# notifications/views.py
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer
from .utils import send_notification


def test_notifications(request):
    return render(request, "test.html")


# notifications/api_views.py


class SendNotificationAPIView(APIView):
    serializer_class = NotificationSerializer

    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user_id"]
            message = serializer.validated_data["message"]

            notification = Notification.objects.create(user=user, message=message)
            notification.save()

            # Send the real-time notification
            send_notification(user.id, message)

            return Response({"detail": "Notification sent!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

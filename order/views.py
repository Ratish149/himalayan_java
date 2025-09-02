from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer


class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only show orders belonging to the logged-in user."""
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Create an order with optional redeem points applied."""
        data = request.data.copy()

        # Prevent overriding another user’s ID
        data['user'] = request.user.id  

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Handle redeem points if provided
        points_to_redeem = int(data.get("points_to_redeem", 0))
        if points_to_redeem > 0:
            if request.user.redeem_points < points_to_redeem:
                return Response(
                    {"error": "Not enough redeem points"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Example: 1 point = 1 unit discount
            discount_value = points_to_redeem
            # Deduct from user balance
            request.user.redeem_points -= points_to_redeem
            request.user.save()

            # Attach discount to order
            serializer.save(user=request.user, discount=discount_value)
        else:
            serializer.save(user=request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Restrict access to only the logged-in user’s orders."""
        return Order.objects.filter(user=self.request.user)

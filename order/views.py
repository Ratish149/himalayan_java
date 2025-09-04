from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
import secrets
from .models import Order
from .serializers import OrderSerializer
from django_filters import rest_framework as filters

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters

def generate_order_number():
    """Generate a unique order number"""
    return f"ORD-{secrets.token_hex(8).upper()}"

class OrderFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="sub_category__category__id", lookup_expr='exact')  # filter products by category id
    sub_category = filters.CharFilter(field_name="sub_category__id", lookup_expr='exact')  # filter products by subcategory id

    class Meta:
        model = Order
        fields = ['category', 'sub_category']

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.SearchFilter]
    filterset_class = OrderFilter

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.id).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Create an order with optional redeem points applied."""
        data = request.data.copy()

        # Prevent overriding another user's ID
        data['user'] = request.user

        # Generate unique order number
        while True:
            order_num = generate_order_number()
            if not Order.objects.filter(order_number=order_num).exists():
                data['order_number'] = order_num
                break

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

    def get_queryset(self):
        """Restrict access to only the logged-in user's orders."""
        return Order.objects.filter(user=self.request.user)
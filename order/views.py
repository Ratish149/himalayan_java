from rest_framework import generics, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderSerializer2, OrderItemSerializer
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters
import secrets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from product.models import Product
from product.serializers import ProductSerializer


def generate_order_number():
    return f"ORD-{secrets.token_hex(8).upper()}"


class OrderFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="items__product__subcategory__category__id", lookup_expr='exact')
    sub_category = filters.CharFilter(field_name="items__product__subcategory__id", lookup_expr='exact')

    class Meta:
        model = Order
        fields = ['category', 'sub_category']


class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.SearchFilter]
    filterset_class = OrderFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer2  # Should include nested items
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        print(self.request.user.full_name)
        data = request.data.copy()
        data['user'] = request.user.id


        # Generate unique order number
        while True:
            order_num = generate_order_number()
            if not Order.objects.filter(order_number=order_num).exists():
                data['order_number'] = order_num
                break

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)



        points_to_redeem = int(data.get("points_to_redeem", 0))
        order = serializer.save(user=request.user)

        # Apply redeem points if used
        if points_to_redeem > 0:
            if self.request.user.redeem_points < points_to_redeem:
                return Response({"error": "Not enough redeem points"}, status=status.HTTP_400_BAD_REQUEST)
            request.user.redeem_points -= points_to_redeem
            request.user.save()
            order.total_price = max(order.total_price - points_to_redeem, 0)
            order.discount = points_to_redeem
            order.save()

        # ✅ Add earned redeem points based on total_price
        earned_points = int(order.total_price // 100)  # 1 point per 100 spent
        request.user.redeem_points += earned_points
        request.user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED, headers=headers)



class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def RecentProductsView(request):

    
    # Get 5 most recent products from user's orders
    recent_products = Product.objects.filter(
        orderitem__order__user=request.user
    ).distinct().order_by('-orderitem__order__created_at')[:5]
    
    serializer = ProductSerializer(recent_products, many=True)
    return Response(serializer.data)


class PastOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).exclude(status__in=['pending', 'confirmed'])
    

class PresentOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, status__in=['pending', 'confirmed'])

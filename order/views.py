from rest_framework import generics, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderSerializer2, OrderItemSerializer
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from product.models import Product
from product.serializers import ProductSerializer

class OrderFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="items__product__sub_category__category__id", lookup_expr='exact')
    sub_category = filters.CharFilter(field_name="items__product__sub_category__id", lookup_expr='exact')

    class Meta:
        model = Order
        fields = ['category', 'sub_category']

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.SearchFilter]
    filterset_class = OrderFilter
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        base_qs = Order.objects.select_related('user', 'branch').prefetch_related(
            'items', 'items__product', 'items__product__sub_category__category'
        )
        if self.request.user and getattr(self.request.user, 'is_staff', False):
            return base_qs
        return base_qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer2
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        print(f"Creating order for user: {self.request.user.full_name}")
        
        # Get points to redeem from request
        points_to_redeem = int(request.data.get("points_to_redeem", 0))
        
        # Validate redeem points before creating order
        if points_to_redeem > 0:
            if self.request.user.redeem_points < points_to_redeem:
                return Response(
                    {"error": "Not enough redeem points"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create the order (serializer handles everything else)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order = serializer.save()
        
        # Apply discount from redeemed points AFTER order creation
        if points_to_redeem > 0:
            request.user.redeem_points -= points_to_redeem
            request.user.save()
            
            # Apply discount to order
            original_total = order.total_price
            order.total_price = max(order.total_price - points_to_redeem, 0)
            order.discount = points_to_redeem
            order.save()
            
            print(f"Applied discount: ${points_to_redeem}, New total: ${order.total_price}")

        headers = self.get_success_headers(serializer.data)
        return Response(
            self.get_serializer(order).data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        base_qs = Order.objects.select_related('user', 'branch').prefetch_related(
            'items', 'items__product', 'items__product__sub_category__category'
        )
        if self.request.user and getattr(self.request.user, 'is_staff', False):
            return base_qs
        return base_qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return OrderSerializer2
        return OrderSerializer

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
    serializer_class = OrderSerializer2
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        base_qs = Order.objects.select_related('user', 'branch').prefetch_related(
            'items', 'items__product', 'items__product__sub_category__category'
        ).exclude(order_status__in=['pending', 'confirmed'])
        if self.request.user and getattr(self.request.user, 'is_staff', False):
            return base_qs
        return base_qs.filter(user=self.request.user)

class PresentOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer2
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        base_qs = Order.objects.select_related('user', 'branch').prefetch_related(
            'items', 'items__product', 'items__product__sub_category__category'
        ).filter(order_status__in=['pending', 'confirmed'])
        if self.request.user and getattr(self.request.user, 'is_staff', False):
            return base_qs
        return base_qs.filter(user=self.request.user)
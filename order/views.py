from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import api_view, permission_classes
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderSerializer2, OrderItemSerializer
from product.models import Product
from product.serializers import ProductSerializer


# -----------------------
# Custom Role Permissions
# -----------------------
class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "superadmin"


class IsBranchAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "admin"


# -----------------------
# Filters
# -----------------------
class OrderFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="items__product__sub_category__category__id", lookup_expr="exact")
    sub_category = filters.CharFilter(field_name="items__product__sub_category__id", lookup_expr="exact")

    class Meta:
        model = Order
        fields = ["category", "sub_category"]


# -----------------------
# Views
# -----------------------
class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.SearchFilter]
    filterset_class = OrderFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = (
            Order.objects.select_related("user", "branch")
            .prefetch_related("items", "items__product", "items__product__sub_category__category")
        )

        # Role-based access
        if getattr(user, "role", None) == "superadmin":
            return base_qs
        elif getattr(user, "role", None) == "admin":
            return base_qs.filter(branch=user.branch)
        else:
            return base_qs.filter(user=user)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        present_orders = queryset.filter(order_status__in=["pending", "confirmed"])
        past_orders = queryset.exclude(order_status__in=["pending", "confirmed"])

        present_serializer = OrderSerializer2(present_orders, many=True)
        past_serializer = OrderSerializer2(past_orders, many=True)
        return Response({
            "present_orders": present_serializer.data,
            "past_orders": past_serializer.data
        })

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderSerializer2
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        print(f"Creating order for user: {request.user.full_name}")

        points_to_redeem = int(request.data.get("points_to_redeem", 0))

        if points_to_redeem > 0:
            if request.user.redeem_points < points_to_redeem:
                return Response(
                    {"error": "Not enough redeem points"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        if points_to_redeem > 0:
            request.user.redeem_points -= points_to_redeem
            request.user.save()

            order.total_price = max(order.total_price - points_to_redeem, 0)
            order.discount = points_to_redeem
            order.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            self.get_serializer(order).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "order_number"

    def get_queryset(self):
        user = self.request.user
        base_qs = (
            Order.objects.select_related("user", "branch")
            .prefetch_related("items", "items__product", "items__product__sub_category__category")
        )

        if getattr(user, "role", None) == "superadmin":
            return base_qs
        elif getattr(user, "role", None) == "admin":
            return base_qs.filter(branch=user.branch)
        else:
            return base_qs.filter(user=user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderSerializer2
        return OrderSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def RecentProductsView(request):
    recent_products = (
        Product.objects.filter(orderitem__order__user=request.user)
        .distinct()
        .order_by("-orderitem__order__created_at")[:5]
    )
    serializer = ProductSerializer(recent_products, many=True)
    return Response(serializer.data)


class PastOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer2
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = (
            Order.objects.select_related("user", "branch")
            .prefetch_related("items", "items__product", "items__product__sub_category__category")
            .exclude(order_status__in=["pending", "confirmed"])
        )

        if getattr(user, "role", None) == "superadmin":
            return base_qs
        elif getattr(user, "role", None) == "admin":
            return base_qs.filter(branch=user.branch)
        else:
            return base_qs.filter(user=user)


class PresentOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer2
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = (
            Order.objects.select_related("user", "branch")
            .prefetch_related("items", "items__product", "items__product__sub_category__category")
            .filter(order_status__in=["pending", "confirmed"])
        )

        if getattr(user, "role", None) == "superadmin":
            return base_qs
        elif getattr(user, "role", None) == "admin":
            return base_qs.filter(branch=user.branch)
        else:
            return base_qs.filter(user=user)

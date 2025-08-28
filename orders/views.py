from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer,OrderItemSerializer
from .models import OrderItem
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from .permissions import IsAdminOrOwner,IsOwnerOfOrderOrAdmin
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from products.models import Product 


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrOwner]
    queryset = Order.objects.all()
    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            self.permission_classes = [IsOwnerOfOrderOrAdmin]
        if self.action in ["destroy"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")

        if prev_status != new_status:
            try:
                with transaction.atomic():  # atomic applies to SQL (Order + OrderItems)
                    for item in order.items.all():
                        # Fetch product from MongoDB
                        try:
                            product = Product.objects.using("products").get(id=item.product_id)
                        except Product.DoesNotExist:
                            return Response(
                                {"error": f"Product {item.product_id} not found in MongoDB."},
                                status=status.HTTP_404_NOT_FOUND,
                            )

                        # If confirming order → reduce stock
                        if new_status == "confirmed" and prev_status != "confirmed":
                            if product.stock >= item.quantity:
                                product.stock -= item.quantity
                                product.save(using="products")
                            else:
                                # Rollback SQL transaction (Order status) if not enough stock
                                raise ValueError(f"Not enough stock for product: {product.name}")

                        # If cancelling a confirmed order → restore stock
                        elif new_status == "cancelled" and prev_status == "confirmed":
                            product.stock += item.quantity
                            product.save(using="products")

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__user=user)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAdminUser]

        if self.action == "create":
            self.permission_classes = [IsOwnerOfOrderOrAdmin]

        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
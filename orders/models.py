from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models import Sum
from products.models import Product  # MongoDB Product
from rest_framework.response import Response

class OrderStatus(models.TextChoices):
    PENDING = "Pending", "pending"
    CONFIRMED = "Confirmed", "confirmed"
    SHIPPED = "Shipped", "shipped"
    DELIVERED = "Delivered", "delivered"
    CANCELLED = "Cancelled", "cancelled"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    shipping_address = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def update_total(self):
        """Recalculate and update total_amount."""
        self.total_amount = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=["total_amount"])


    def __str__(self):
        return f"Order {self.id} - {self.user} ({self.status})"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.UUIDField()
    quantity = models.PositiveIntegerField()

    def details(self):
        product = Product.objects.using("products").get(id=self.product_id)
        return {
            "product_id": self.product_id,
            "product_name": product.name,
            "price": product.price,
            "features": product.features
        }

    @property
    def subtotal(self):
        return self.details()["price"] * self.quantity

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # update total on order when item is saved
        self.order.update_total()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # update total on order when item is deleted
        self.order.update_total()

    def __str__(self):
        return f"{self.details()['product_name']} x {self.quantity} (Order {self.order.id})"

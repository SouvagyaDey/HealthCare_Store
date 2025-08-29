from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models import Sum
from products.models import ProductStore
from products.models import Product

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
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} - {self.user} ({self.status})"
    
    def update_total(self):
        self.total_amount = self.order_items.aggregate(
            total=Sum(models.F("price") * models.F("quantity"))
        )["total"] or 0
        self.save(update_fields=["total_amount"])


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(ProductStore, on_delete=models.CASCADE, related_name="product_items")
    quantity = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def price(self):
        try:
            product = Product.objects.using("Products").get(id=self.product.id)
            return product.price
        except Product.DoesNotExist:
            return None

    @property
    def subtotal(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        self.order.update_total()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.order.update_total()

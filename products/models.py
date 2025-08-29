from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
import uuid

class ProductCategory(models.TextChoices):
    MEDICINE = "Medicine", "medicine"
    EQUIPMENT = "Equipment", "equipment"
    WELLNESS = "Wellness", "wellness"
    FITNESS = "Fitness", "fitness"

class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=100,
        choices=ProductCategory.choices,
        default=ProductCategory.MEDICINE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    manufacturer = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # Dynamic attributes per category (Mongo-friendly)
    features = models.JSONField(default=dict, blank=False,)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_available(self):
        return "Available" if self.stock > 0 else "Out of Stock"

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        managed = False

        constraints = [
            models.CheckConstraint(
                name='price_non_negative',
                check=Q(price__gte=0),
                violation_error_message='Price must be a non-negative number.'
            )
        ]

        
    def delete(self, using=None, keep_parents=False):
        ProductStore.objects.filter(product_id=self.id).delete()
        super().delete(using="products", keep_parents=keep_parents)

    def __str__(self):
        return f"{self.name} ({self.category})"
    

class ProductStore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.UUIDField()
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def product(self):
        try:
            return Product.objects.using("products").get(id=self.product_id)
        except Product.DoesNotExist:
            return None
    

class ProductReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProductStore, on_delete=models.CASCADE,related_name='product_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='rating_between_1_and_5',
                check=Q(rating__gte=1, rating__lte=5),
                violation_error_message='Rating must be between 1 and 5.'
            )
        ]
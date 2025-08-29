from django.contrib import admin
from .models import Product, ProductStore


admin.site.register(Product)
admin.site.register(ProductStore)
from django.shortcuts import render
from rest_framework import viewsets
from products.models import ProductStore,Product
from products.serializers import ProductSerializer, ProductStoreSerializer
from rest_framework.permissions import IsAdminUser,AllowAny


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]


class ProductStoreViewSet(viewsets.ModelViewSet):
    queryset = ProductStore.objects.all()
    serializer_class = ProductStoreSerializer
    permission_classes = [IsAdminUser]  

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
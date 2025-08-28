from django.shortcuts import render
from rest_framework import viewsets
from products.models import ProductStore
from products.serializers import ProductStoreSerializer
from rest_framework.permissions import IsAdminUser,AllowAny
# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductStore.objects.all()
    serializer_class = ProductStoreSerializer
    permission_classes = [IsAdminUser]  

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
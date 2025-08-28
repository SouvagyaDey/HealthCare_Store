from rest_framework import serializers
from products.models import Product, ProductStore


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id','name','category',
            'price','manufacturer','description',
            'features','created_at','updated_at'
        ]



class ProductStoreSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # returns Mongo product
    product_data = ProductSerializer(write_only=True)  # accepts nested product

    class Meta:
        model = ProductStore
        fields = ["id", "product", "product_data", "stock", "created_at", "updated_at"]

    def create(self, validated_data):
        product_data = validated_data.pop("product_data")

        # create product in Mongo
        product = Product.objects.using("products").create(**product_data)

        # store reference in SQL
        return ProductStore.objects.create(product_id=product.id, **validated_data)

    def update(self, instance, validated_data):
        product_data = validated_data.pop("product_data", None)

        if product_data:
            product = Product.objects.using("products").get(id=instance.product_id)
            for attr, value in product_data.items():
                setattr(product, attr, value)
            product.save(using="products")

        return super().update(instance, validated_data)

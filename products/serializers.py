from rest_framework import serializers
from products.models import Product, ProductStore


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    features = serializers.JSONField(required=True)
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
    product = ProductSerializer(read_only=True)
    product_data = ProductSerializer(write_only=True,required=False)

    class Meta:
        model = ProductStore
        fields = ["id", "product", "product_data", "stock", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is None:  
            self.fields["product_data"].required = True
        

    def create(self, validated_data):
        product_data = validated_data.pop("product_data", None)
        if not product_data:
            raise serializers.ValidationError({"product_data": "This field is required."})

        product = Product.objects.using("products").create(**product_data)
        return ProductStore.objects.create(product_id=product.id, **validated_data)

    def update(self, instance, validated_data):
        product_data = validated_data.pop("product_data", None)

        if product_data:
            product = Product.objects.using("products").get(id=instance.product_id)
            for attr, value in product_data.items():
                setattr(product, attr, value)
            product.save(using="products")

        return super().update(instance, validated_data)

from rest_framework import serializers
from orders.models import Order, OrderItem
from products.models import Product  # MongoDB product


class OrderItemSerializer(serializers.ModelSerializer):

    id = serializers.UUIDField(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    details = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product_id",
            "quantity",
            "subtotal",
            'details'
        ]


        extra_kwargs = {
            "order": {"read_only": True},
            "subtotal": {"read_only": True},
            "details": {"read_only": True}
        }

    def get_details(self, obj):
        return obj.details()


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    order_date = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    items = OrderItemSerializer(many=True)  # single field for read & write

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "shipping_address",
            "order_date",
            "updated_at",
            "total_amount",
            "items",
        ]

    def get_total_amount(self, obj):
        return sum(item.subtotal for item in obj.items.all())

    def create(self, validated_data):
        items_data = validated_data.pop("items", None)

        if not items_data:
            raise serializers.ValidationError({"items": "Order must contain at least one item."})

        order = Order.objects.create(**validated_data)

        for item in items_data:
            product_uuid = item.pop("product_id")
            try:
                product = Product.objects.using("products").get(id=product_uuid)
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product": "Product does not exist."})

            quantity = item.get("quantity", 1)

            OrderItem.objects.create(
                order=order,
                product_id=product.id,
                quantity=quantity,
            )

        return order

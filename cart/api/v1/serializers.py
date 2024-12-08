from rest_framework import serializers

from cart.models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'product_name', 'product_price', 'total_price']

class AddToCartSerializer(serializers.Serializer):
    """
    Serializer for adding a product to the cart.
    """
    product_id = serializers.IntegerField(required=True, help_text="ID of the product to add to the cart.")

class CartItemListingSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2)
    available_stock = serializers.IntegerField(source="product.stock")
    out_of_stock = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "product_price", "quantity", "available_stock", "out_of_stock"]

    def get_out_of_stock(self, obj):
        return obj.quantity > obj.product.stock


class CheckoutResponseSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(help_text="ID of the created order.")
    total_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Total value of the order."
    )
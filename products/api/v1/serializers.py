from rest_framework import serializers

from products.models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'product_count']
        read_only_fields = ['id', 'product_count']

    def validate_name(self, value):
        """
        Ensure the category name is unique
        """
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku',
            'price', 'stock', 'is_active', 'category',
            'category_name', 'image', 'featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

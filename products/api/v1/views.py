from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from basics.api.v1.views import BaseAPIView
from .serializers import ProductSerializer, CategorySerializer
from ...models import Product, Category

class ProductListCreateAPIView(BaseAPIView):
    """
    Handles listing all products and creating a new product.
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page",
                              type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request):
        """
        Get the paginated list of products.
        """
        # Fetch the products with filters
        products = Product.objects.filter(is_active=True).order_by('name')
        paginator, paginated_products = self.get_paginated_data(products, request)
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=ProductSerializer,
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(data=serializer.data, message="Product created successfully.", status_code=status.HTTP_201_CREATED)
        return self.failure_response(error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class ProductRetrieveUpdateDeleteAPIView(BaseAPIView):
    """
    Handles retrieving, updating, and deleting a specific product.
    """
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, is_active=True)
        serializer = ProductSerializer(product)
        return self.success_response(data=serializer.data, message="Product retrieved successfully.")

    @swagger_auto_schema(
        request_body=ProductSerializer,
    )
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(data=serializer.data, message="Product updated successfully.")
        return self.failure_response(error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return self.success_response(message="Product deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)


class CategoryListView(BaseAPIView):

    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of categories.
        """
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return self.success_response(data=serializer.data, message="Categories retrieved successfully.")

    @swagger_auto_schema(
        request_body=CategorySerializer,
    )
    def post(self, request, *args, **kwargs):
        """
        Create a new category.
        """
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return self.success_response(
                data=CategorySerializer(category).data,
                message="Category created successfully.",
                status_code=201
            )
        return self.failure_response(error=serializer.errors, status_code=400)

class CategoryDetailView(BaseAPIView):
    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve a specific category by ID.
        """
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return self.success_response(data=serializer.data, message="Category retrieved successfully.")
        except Category.DoesNotExist:
            return self.failure_response(error="Category not found.", status_code=404)

    @swagger_auto_schema(
        request_body=CategorySerializer,
    )
    def put(self, request, pk, *args, **kwargs):
        """
        Update an existing category.
        """
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return self.failure_response(error="Category not found.", status_code=404)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            updated_category = serializer.save()
            return self.success_response(
                data=CategorySerializer(updated_category).data,
                message="Category updated successfully."
            )
        return self.failure_response(error=serializer.errors, status_code=400)

    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a specific category by ID.
        """
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return self.success_response(message="Category deleted successfully.")
        except Category.DoesNotExist:
            return self.failure_response(error="Category not found.", status_code=404)

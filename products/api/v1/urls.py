from django.urls import path
from .views import ProductListCreateAPIView, ProductRetrieveUpdateDeleteAPIView, CategoryListView, CategoryDetailView

urlpatterns = [
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDeleteAPIView.as_view(), name='product-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),  # For listing and creating categories
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]

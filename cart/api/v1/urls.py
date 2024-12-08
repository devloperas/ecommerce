from django.urls import path

from cart.api.v1.views import AddToCartAPIView, CartListingAPIView, RemoveFromCartAPIView, CheckoutAPIView

urlpatterns = [
    # path('cart/', CartItemListCreateAPIView.as_view(), name='cart-list-create'),
    # path('cart/<int:pk>/', CartItemUpdateDeleteAPIView.as_view(), name='cart-update-delete'),
    path('cart/add/', AddToCartAPIView.as_view(), name='add-to-cart'),
    path('cart/remove/', RemoveFromCartAPIView.as_view(), name='remove-from-cart'),
    path('cart/list/', CartListingAPIView.as_view(), name='cart-list'),
    path('cart/checkout/', CheckoutAPIView.as_view(), name='checkout-cart'),
]
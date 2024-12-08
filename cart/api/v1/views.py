from rest_framework import status
from rest_framework.exceptions import ValidationError

from basics.api.v1.views import BaseAPIView
from products.models import Product
from .serializers import AddToCartSerializer, CartItemListingSerializer, CheckoutResponseSerializer
from django.db import transaction
from cart.models import CartItem, Cart, OrderItem, Order
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class AddToCartAPIView(BaseAPIView):
    """
    Handles adding a product to the cart.
    """

    @swagger_auto_schema(request_body=AddToCartSerializer)
    def post(self, request):
        # Extract the product ID from the request data
        product_id = request.data.get("product_id")
        if not product_id:
            return self.failure_response(error="Product ID is required.", status_code=status.HTTP_400_BAD_REQUEST)

        # Validate that the product exists
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return self.failure_response(error="Product not found.", status_code=status.HTTP_404_NOT_FOUND)

        # Check if the product is in stock
        if product.stock < 1:
            return self.failure_response(error=f"{product.name} is out of stock.", status_code=status.HTTP_400_BAD_REQUEST)

        # Get or create a cart for the user
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the product is already in the cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": 1}
        )

        if not item_created:
            # If the item already exists, increment the quantity
            new_quantity = cart_item.quantity + 1
            if new_quantity > product.stock:
                return self.failure_response(
                    error=f"Product is out of stock!",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            cart_item.quantity = new_quantity
            cart_item.save()

        return self.success_response(
            data={"cart_item": AddToCartSerializer(cart_item).data},
            message="Product added to cart successfully.",
            status_code=status.HTTP_201_CREATED,
        )

class RemoveFromCartAPIView(BaseAPIView):
    """
    Handles removing a product from the cart or reducing its quantity based on the 'remove' parameter.
    """

    @swagger_auto_schema(request_body=AddToCartSerializer)
    def post(self, request):
        # Extract product ID and remove parameter from the request data
        product_id = request.data.get("product_id")
        remove = request.data.get("remove", False)  # Default to False if not provided

        if not product_id:
            return self.failure_response(error="Product ID is required.", status_code=status.HTTP_400_BAD_REQUEST)

        # Get the user's cart
        try:
            cart = Cart.objects.prefetch_related("items").get(user=request.user)
        except Cart.DoesNotExist:
            return self.failure_response(error="Cart not found.", status_code=status.HTTP_404_NOT_FOUND)

        # Check if the product exists in the cart
        try:
            cart_item = cart.items.get(product_id=product_id)
        except CartItem.DoesNotExist:
            return self.failure_response(error="Product not found in the cart.", status_code=status.HTTP_404_NOT_FOUND)

        # Handle removal based on the 'remove' parameter
        if remove:
            cart_item.delete()
            message = f"Removed {cart_item.product.name} from the cart."
        else:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                message = f"Reduced quantity of {cart_item.product.name} to {cart_item.quantity}."
            else:
                cart_item.delete()
                message = f"Removed {cart_item.product.name} from the cart."

        return self.success_response(
            message=message,
            status_code=status.HTTP_200_OK,
        )


class CartListingAPIView(BaseAPIView):
    """
    Handles listing all items in the user's cart.
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page",
                              type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request):
        # Fetch the user's cart
        try:
            cart = Cart.objects.prefetch_related("items__product").get(user=request.user)
        except Cart.DoesNotExist:
            return self.success_response(data=[], message="Your cart is empty.")

        # Serialize cart items
        cart_items = cart.items.all()
        paginator, paginated_items = self.get_paginated_data(cart_items, request)
        serializer = CartItemListingSerializer(paginated_items, many=True)

        return paginator.get_paginated_response(serializer.data, "Cart items retrieved successfully.")


class CheckoutAPIView(BaseAPIView):
    """
    API view for checking out a user's cart and creating an order.
    """

    @swagger_auto_schema(responses={201: CheckoutResponseSerializer})
    def post(self, request):
        try:
            # Fetch the user's cart
            try:
                cart = Cart.objects.prefetch_related("items__product").get(user=request.user)
            except Cart.DoesNotExist:
                return self.failure_response(
                    error="Cart is empty.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if not cart.items.exists():
                return self.failure_response(
                    error="Cart is empty.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Validate stock and create order
            with transaction.atomic():
                order = Order.objects.create(user=request.user, total_value=0)

                total_value = 0
                for cart_item in cart.items.all():
                    product = cart_item.product
                    quantity = cart_item.quantity

                    # Check stock availability
                    if quantity > product.stock:
                        raise ValidationError(f"Not enough stock for {product.name}.")

                    total_price = product.price * quantity

                    # Reduce stock
                    product.stock -= quantity
                    product.save()

                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product_name=product.name,
                        product_price=product.price,
                        quantity=quantity,
                        total_price=total_price,
                    )

                    total_value += total_price

                # Update order's total value
                order.total_value = total_value
                order.save()

                # Clear the user's cart
                cart.items.all().delete()

            return self.success_response(
                data={"order_id": order.id, "total_value": total_value},
                message="Order placed successfully.",
                status_code=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            return self.failure_response(
                error=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return self.failure_response(
                error="An unexpected error occurred. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

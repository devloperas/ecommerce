from django.db import models
from rest_framework.exceptions import ValidationError

from core.models import BaseModel
from products.models import Product
from user.models import User


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.first_name} {self.user.last_name}"

    def total(self):
        return sum(item.total_price() for item in self.items.all())


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def total_price(self):
        return self.quantity * self.product.price

    def clean(self):
        """
        Custom validation to check the stock when adding or updating cart items.
        This does NOT reduce stock on adding to cart; stock is only updated on checkout.
        """
        if self.quantity > self.product.stock:
            raise ValidationError(f"Product out of stock")

        max_quantity = 10  # Optional: you can also define a max quantity per product
        if self.quantity > max_quantity:
            raise ValidationError(f"Cannot add more than {max_quantity} of {self.product.name} to the cart.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Order(models.Model):
    """
    Represents an order placed by a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='PENDING'
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - Total: {self.total_value}"

    def calculate_total_value(self):
        """
        Calculate the total value of the order based on its items.
        """
        return sum(item.total_price for item in self.items.all())

class OrderItem(models.Model):
    """
    Represents an individual item in an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity} (Order {self.order.id})"

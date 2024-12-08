from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_("Category Name"), unique=True)
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    product_count = models.PositiveIntegerField(default=0, verbose_name=_("Product Count"))

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class Product(BaseModel, PermissionsMixin):
    name = models.CharField(max_length=255, verbose_name=_("Product Name"))
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    sku = models.CharField(max_length=100, verbose_name=_("SKU"), unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    stock = models.PositiveIntegerField(verbose_name=_("Stock Quantity"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Category"),
    )
    image = models.ImageField(upload_to='products/', verbose_name=_("Product Image"), blank=True, null=True)
    featured = models.BooleanField(default=False, verbose_name=_("Featured Product"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        permissions = [
            ("can_mark_as_featured", "Can mark product as featured"),
        ]

    def __str__(self):
        return self.name


# Signals to update product count
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_product_count(sender, instance, **kwargs):
    """
    Updates the product count for a category whenever a product is added, updated, or deleted.
    """
    category = instance.category
    if category:
        category.product_count = category.products.count()
        category.save()

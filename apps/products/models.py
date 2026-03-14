from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def in_stock(self):
        return self.filter(stock_quantity__gt=0)

    def by_category(self, category_slug: str):
        return self.filter(category__slug=category_slug)

    def affordable(self, max_price):
        return self.filter(price__lte=max_price)


class Product(TimeStampedModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    is_active = models.BooleanField(default=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0

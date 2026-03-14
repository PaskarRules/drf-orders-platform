from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "stock_quantity", "category", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}

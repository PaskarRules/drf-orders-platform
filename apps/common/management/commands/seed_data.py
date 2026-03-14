import os
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.products.models import Category, Product

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with sample data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # Admin user
        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                email="admin@example.com",
                username="admin",
                password=os.environ.get("SEED_ADMIN_PASSWORD", "admin123456"),
            )
            self.stdout.write(self.style.SUCCESS("Created admin user"))

        # Regular user
        if not User.objects.filter(email="user@example.com").exists():
            User.objects.create_user(
                email="user@example.com",
                username="testuser",
                password=os.environ.get("SEED_USER_PASSWORD", "user123456"),
            )
            self.stdout.write(self.style.SUCCESS("Created test user"))

        # Categories
        categories_data = ["Electronics", "Books", "Clothing", "Home & Garden", "Sports"]
        categories = {}
        for name in categories_data:
            cat, created = Category.objects.get_or_create(name=name)
            categories[name] = cat
            if created:
                self.stdout.write(f"  Created category: {name}")

        # Products
        products_data = [
            ("Wireless Headphones", "wireless-headphones", "ELEC-001", Decimal("79.99"), 50, "Electronics"),
            ("Bluetooth Speaker", "bluetooth-speaker", "ELEC-002", Decimal("49.99"), 30, "Electronics"),
            ("USB-C Cable", "usb-c-cable", "ELEC-003", Decimal("12.99"), 200, "Electronics"),
            ("Python Crash Course", "python-crash-course", "BOOK-001", Decimal("39.99"), 100, "Books"),
            ("Clean Code", "clean-code", "BOOK-002", Decimal("34.99"), 75, "Books"),
            ("Running Shoes", "running-shoes", "CLTH-001", Decimal("129.99"), 25, "Clothing"),
            ("Cotton T-Shirt", "cotton-t-shirt", "CLTH-002", Decimal("19.99"), 150, "Clothing"),
            ("Garden Tools Set", "garden-tools-set", "HOME-001", Decimal("59.99"), 40, "Home & Garden"),
            ("Yoga Mat", "yoga-mat", "SPRT-001", Decimal("29.99"), 80, "Sports"),
            ("Basketball", "basketball", "SPRT-002", Decimal("24.99"), 60, "Sports"),
        ]

        for name, slug, sku, price, stock, cat_name in products_data:
            _, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "slug": slug,
                    "price": price,
                    "stock_quantity": stock,
                    "category": categories[cat_name],
                },
            )
            if created:
                self.stdout.write(f"  Created product: {name}")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

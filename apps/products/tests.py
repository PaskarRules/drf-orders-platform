import pytest
from decimal import Decimal

from django.urls import reverse

from apps.products.models import Category, Product

PRODUCT_LIST_URL = reverse("products:product-list")
CATEGORY_LIST_URL = reverse("products:category-list")


def product_detail_url(slug):
    return reverse("products:product-detail", kwargs={"slug": slug})


@pytest.mark.django_db
class TestProductAPI:
    def test_list_unauthenticated(self, api_client, product):
        response = api_client.get(PRODUCT_LIST_URL)
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_detail(self, api_client, product):
        response = api_client.get(product_detail_url(product.slug))
        assert response.status_code == 200
        assert response.data["sku"] == product.sku
        assert response.data["category_name"] == product.category.name

    def test_filter_by_category(self, api_client, product):
        response = api_client.get(PRODUCT_LIST_URL, {"category": "electronics"})
        assert response.data["count"] == 1

    def test_filter_by_price_range(self, api_client, product):
        response = api_client.get(PRODUCT_LIST_URL, {"min_price": 20, "max_price": 40})
        assert response.data["count"] == 1
        response = api_client.get(PRODUCT_LIST_URL, {"min_price": 50})
        assert response.data["count"] == 0

    def test_filter_in_stock(self, api_client, product):
        response = api_client.get(PRODUCT_LIST_URL, {"in_stock": "true"})
        assert response.data["count"] == 1

    def test_filter_out_of_stock(self, api_client, product):
        product.stock_quantity = 0
        product.save()
        response = api_client.get(PRODUCT_LIST_URL, {"in_stock": "false"})
        assert response.data["count"] == 1

    def test_search(self, api_client, product):
        response = api_client.get(PRODUCT_LIST_URL, {"search": "Test"})
        assert response.data["count"] == 1
        response = api_client.get(PRODUCT_LIST_URL, {"search": "nonexistent"})
        assert response.data["count"] == 0

    def test_ordering(self, api_client, category):
        Product.objects.create(name="Cheap", slug="cheap", sku="C-1", price="5.00", stock_quantity=1, category=category)
        Product.objects.create(name="Expensive", slug="expensive", sku="E-1", price="500.00", stock_quantity=1, category=category)
        response = api_client.get(PRODUCT_LIST_URL, {"ordering": "price"})
        prices = [r["price"] for r in response.data["results"]]
        assert prices == sorted(prices)

    def test_inactive_products_hidden(self, api_client, product):
        product.is_active = False
        product.save()
        response = api_client.get(PRODUCT_LIST_URL)
        assert response.data["count"] == 0

    def test_create_requires_admin(self, auth_client, category):
        response = auth_client.post(PRODUCT_LIST_URL, {
            "name": "New", "sku": "N-1", "price": "19.99",
            "stock_quantity": 10, "category": category.id,
        })
        assert response.status_code == 403

    def test_create_admin(self, admin_client, category):
        response = admin_client.post(PRODUCT_LIST_URL, {
            "name": "New Product", "slug": "new-product", "sku": "NEW-001",
            "price": "19.99", "stock_quantity": 10, "category": category.id,
        })
        assert response.status_code == 201

    def test_update_admin(self, admin_client, product):
        response = admin_client.patch(
            product_detail_url(product.slug),
            {"price": "49.99"},
        )
        assert response.status_code == 200
        product.refresh_from_db()
        assert product.price == Decimal("49.99")

    def test_delete_admin(self, admin_client, product):
        response = admin_client.delete(product_detail_url(product.slug))
        assert response.status_code == 204
        assert not Product.objects.filter(id=product.id).exists()

    def test_detail_nonexistent(self, api_client):
        response = api_client.get(product_detail_url("no-such-slug"))
        assert response.status_code == 404


@pytest.mark.django_db
class TestCategoryAPI:
    def test_list(self, api_client, category):
        response = api_client.get(CATEGORY_LIST_URL)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_create_requires_admin(self, auth_client):
        response = auth_client.post(CATEGORY_LIST_URL, {"name": "Books"})
        assert response.status_code == 403

    def test_create_admin(self, admin_client):
        response = admin_client.post(CATEGORY_LIST_URL, {"name": "Books"})
        assert response.status_code == 201
        assert Category.objects.filter(name="Books").exists()

    def test_auto_slug_generation(self, db):
        cat = Category.objects.create(name="Home & Garden")
        assert cat.slug == "home-garden"


# ── QuerySet tests ───────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestProductQuerySet:
    def test_active(self, product):
        assert Product.objects.active().count() == 1
        product.is_active = False
        product.save()
        assert Product.objects.active().count() == 0

    def test_in_stock(self, product):
        assert Product.objects.in_stock().count() == 1
        product.stock_quantity = 0
        product.save()
        assert Product.objects.in_stock().count() == 0

    def test_by_category(self, product):
        assert Product.objects.by_category("electronics").count() == 1
        assert Product.objects.by_category("books").count() == 0

    def test_affordable(self, product):
        assert Product.objects.affordable(Decimal("30.00")).count() == 1
        assert Product.objects.affordable(Decimal("10.00")).count() == 0

    def test_chaining(self, product):
        qs = Product.objects.active().in_stock().by_category("electronics")
        assert qs.count() == 1


# ── Model property tests ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestProductModel:
    def test_str(self, product):
        assert str(product) == product.name

    def test_is_in_stock_true(self, product):
        assert product.is_in_stock is True

    def test_is_in_stock_false(self, product):
        product.stock_quantity = 0
        product.save()
        assert product.is_in_stock is False

    def test_category_str(self, category):
        assert str(category) == category.name

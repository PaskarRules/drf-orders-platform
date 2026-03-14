from contextlib import contextmanager

import factory
import pytest
from django.db.models.signals import post_save
from rest_framework.test import APIClient

USER_PASSWORD = "testpass123"
ADMIN_PASSWORD = "adminpass123"


# ── Factories ────────────────────────────────────────────────────────────────


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.User"

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", USER_PASSWORD)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "products.Category"

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "products.Product"

    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    sku = factory.Sequence(lambda n: f"SKU-{n:04d}")
    price = "29.99"
    stock_quantity = 100
    category = factory.SubFactory(CategoryFactory)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory(
        email="test@example.com",
        username="testuser",
    )


@pytest.fixture
def admin_user(db):
    u = UserFactory(
        email="admin@example.com",
        username="admin",
        is_staff=True,
        is_superuser=True,
    )
    u.set_password(ADMIN_PASSWORD)
    u.save(update_fields=["password"])
    return u


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def category(db):
    return CategoryFactory(name="Electronics", slug="electronics")


@pytest.fixture
def product(db, category):
    return ProductFactory(
        name="Test Product",
        slug="test-product",
        sku="TEST-001",
        price="29.99",
        stock_quantity=100,
        category=category,
    )


@pytest.fixture(autouse=True)
def _celery_eager(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@contextmanager
def _disconnect_order_signal():
    """Temporarily disconnect the order post_save signal."""
    from apps.orders.models import Order
    from apps.orders.signals import order_post_save

    post_save.disconnect(order_post_save, sender=Order)
    try:
        yield
    finally:
        post_save.connect(order_post_save, sender=Order)


@pytest.fixture
def mute_order_signal():
    """Fixture that prevents the process_order task from firing on order creation."""
    with _disconnect_order_signal():
        yield

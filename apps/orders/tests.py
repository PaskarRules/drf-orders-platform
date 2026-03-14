import pytest
from decimal import Decimal

from django.urls import reverse

from apps.orders.exceptions import InsufficientStockError, InvalidOrderStateError, ProductNotFoundError
from apps.orders.models import Order
from apps.orders.services import create_order, cancel_order

ORDER_LIST_URL = reverse("orders:order-list-create")


def order_detail_url(order_number):
    return reverse("orders:order-detail", kwargs={"order_number": order_number})


def order_cancel_url(order_number):
    return reverse("orders:order-cancel", kwargs={"order_number": order_number})


@pytest.mark.django_db
class TestCreateOrderAPI:
    def test_success(self, auth_client, product):
        response = auth_client.post(
            ORDER_LIST_URL,
            {"items": [{"product_id": product.id, "quantity": 2}]},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["order_number"].startswith("ORD-")
        assert response.data["total_amount"] == "59.98"
        product.refresh_from_db()
        assert product.stock_quantity == 98

    def test_insufficient_stock(self, auth_client, product):
        response = auth_client.post(
            ORDER_LIST_URL,
            {"items": [{"product_id": product.id, "quantity": 999}]},
            format="json",
        )
        assert response.status_code == 409

    def test_nonexistent_product(self, auth_client):
        response = auth_client.post(
            ORDER_LIST_URL,
            {"items": [{"product_id": 99999, "quantity": 1}]},
            format="json",
        )
        assert response.status_code == 400

    def test_unauthenticated(self, api_client, product):
        response = api_client.post(
            ORDER_LIST_URL,
            {"items": [{"product_id": product.id, "quantity": 1}]},
            format="json",
        )
        assert response.status_code == 401

    def test_empty_items(self, auth_client):
        response = auth_client.post(
            ORDER_LIST_URL,
            {"items": []},
            format="json",
        )
        assert response.status_code == 400

    def test_multiple_items(self, auth_client, category):
        from apps.products.models import Product
        p1 = Product.objects.create(
            name="A", slug="a", sku="A-001", price="10.00",
            stock_quantity=50, category=category,
        )
        p2 = Product.objects.create(
            name="B", slug="b", sku="B-001", price="20.00",
            stock_quantity=50, category=category,
        )
        response = auth_client.post(
            ORDER_LIST_URL,
            {"items": [
                {"product_id": p1.id, "quantity": 3},
                {"product_id": p2.id, "quantity": 2},
            ]},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["total_amount"] == "70.00"


@pytest.mark.django_db
class TestOrderListAPI:
    def test_list_own_orders(self, auth_client, user, product):
        create_order(user, [{"product_id": product.id, "quantity": 1}])
        response = auth_client.get(ORDER_LIST_URL)
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_unauthenticated(self, api_client):
        response = api_client.get(ORDER_LIST_URL)
        assert response.status_code == 401

    def test_admin_sees_all_orders(self, admin_client, user, product):
        create_order(user, [{"product_id": product.id, "quantity": 1}])
        response = admin_client.get(ORDER_LIST_URL)
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestOrderDetailAPI:
    def test_get_order_detail(self, auth_client, user, product):
        order = create_order(user, [{"product_id": product.id, "quantity": 1}])
        response = auth_client.get(order_detail_url(order.order_number))
        assert response.status_code == 200
        assert response.data["order_number"] == order.order_number
        assert len(response.data["items"]) == 1

    def test_nonexistent_order(self, auth_client):
        response = auth_client.get(order_detail_url("ORD-00000000-00000"))
        assert response.status_code == 404


@pytest.mark.django_db
class TestCancelOrderAPI:
    def test_cancel_pending_order(self, auth_client, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 5}])
        response = auth_client.post(order_cancel_url(order.order_number))
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED
        product.refresh_from_db()
        assert product.stock_quantity == 100

    def test_cancel_completed_order_fails(self, auth_client, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 1}])
        order.status = Order.Status.COMPLETED
        order.save()
        response = auth_client.post(order_cancel_url(order.order_number))
        assert response.status_code == 409

    def test_cancel_nonexistent_order(self, auth_client):
        response = auth_client.post(order_cancel_url("ORD-00000000-99999"))
        assert response.status_code == 404


# ── Service layer unit tests ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestOrderService:
    def test_order_number_format(self, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 1}])
        parts = order.order_number.split("-")
        assert parts[0] == "ORD"
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 8  # random digits

    def test_insufficient_stock_raises_custom_exception(self, user, product):
        with pytest.raises(InsufficientStockError):
            create_order(user, [{"product_id": product.id, "quantity": 999}])

    def test_inactive_product_raises_not_found(self, user, product):
        product.is_active = False
        product.save()
        with pytest.raises(ProductNotFoundError):
            create_order(user, [{"product_id": product.id, "quantity": 1}])

    def test_cancel_completed_raises_invalid_state(self, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 1}])
        order.status = Order.Status.COMPLETED
        order.save()
        with pytest.raises(InvalidOrderStateError):
            cancel_order(order)

    def test_stock_restored_on_cancel(self, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 10}])
        assert product.stock_quantity == 100  # fixture has 100
        product.refresh_from_db()
        assert product.stock_quantity == 90
        cancel_order(order)
        product.refresh_from_db()
        assert product.stock_quantity == 100


# ── QuerySet manager tests ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestOrderQuerySet:
    def test_pending_filter(self, user, product, mute_order_signal):
        create_order(user, [{"product_id": product.id, "quantity": 1}])
        assert Order.objects.pending().count() == 1

    def test_completed_filter(self, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 1}])
        order.status = Order.Status.COMPLETED
        order.save()
        assert Order.objects.completed().count() == 1
        assert Order.objects.pending().count() == 0

    def test_for_user(self, user, admin_user, product, mute_order_signal):
        create_order(user, [{"product_id": product.id, "quantity": 1}])
        assert Order.objects.for_user(user).count() == 1
        assert Order.objects.for_user(admin_user).count() == 0

    def test_total_revenue(self, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 2}])
        order.status = Order.Status.COMPLETED
        order.save()
        assert Order.objects.total_revenue() == Decimal("59.98")

    def test_total_revenue_excludes_non_completed(self, user, product, mute_order_signal):
        create_order(user, [{"product_id": product.id, "quantity": 1}])  # pending
        assert Order.objects.total_revenue() == 0

    def test_with_items(self, user, product, mute_order_signal):
        create_order(user, [{"product_id": product.id, "quantity": 1}])
        order = Order.objects.with_items().first()
        # prefetched — no additional queries
        assert len(order.items.all()) == 1


# ── Model property tests ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestOrderModelProperties:
    def test_is_cancellable_pending(self, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 1}])
        assert order.is_cancellable is True

    def test_is_cancellable_processing(self, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 1}])
        order.status = Order.Status.PROCESSING
        order.save()
        assert order.is_cancellable is True

    def test_not_cancellable_completed(self, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 1}])
        order.status = Order.Status.COMPLETED
        order.save()
        assert order.is_cancellable is False

    def test_item_count(self, user, product, category, mute_order_signal):
        from apps.products.models import Product as P
        p2 = P.objects.create(
            name="Other", slug="other", sku="O-1", price="5.00",
            stock_quantity=10, category=category,
        )
        order = create_order(user, [
            {"product_id": product.id, "quantity": 1},
            {"product_id": p2.id, "quantity": 2},
        ])
        assert order.item_count == 2

    def test_str(self, user, product, mute_order_signal):
        order = create_order(user, [{"product_id": product.id, "quantity": 1}])
        assert str(order) == order.order_number

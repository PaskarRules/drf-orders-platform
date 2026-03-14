import pytest
from django.urls import reverse

from apps.notifications.models import Notification
from apps.notifications.tasks import send_order_notification
from apps.orders.services import create_order

NOTIFICATION_LIST_URL = reverse("notifications:notification-list")
MARK_READ_URL = reverse("notifications:mark-read")
UNREAD_COUNT_URL = reverse("notifications:unread-count")


@pytest.fixture
def order(user, product, mute_order_signal):
    return create_order(user, [{"product_id": product.id, "quantity": 1}])


@pytest.fixture
def notification(user, order):
    return Notification.objects.create(
        user=user,
        notification_type=Notification.NotificationType.ORDER_COMPLETED,
        title="Order Completed",
        message=f"Your order {order.order_number} has been completed.",
        order=order,
    )


@pytest.mark.django_db
class TestNotificationList:
    def test_list_own_notifications(self, auth_client, notification):
        response = auth_client.get(NOTIFICATION_LIST_URL)
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "Order Completed"

    def test_filter_unread(self, auth_client, notification):
        response = auth_client.get(NOTIFICATION_LIST_URL, {"is_read": "false"})
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_filter_read_empty(self, auth_client, notification):
        response = auth_client.get(NOTIFICATION_LIST_URL, {"is_read": "true"})
        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_unauthenticated(self, api_client):
        response = api_client.get(NOTIFICATION_LIST_URL)
        assert response.status_code == 401

    def test_cannot_see_other_users_notifications(self, admin_client, notification):
        """Admin should not see another user's notifications via this endpoint."""
        response = admin_client.get(NOTIFICATION_LIST_URL)
        assert response.status_code == 200
        assert response.data["count"] == 0


@pytest.mark.django_db
class TestMarkRead:
    def test_mark_specific_as_read(self, auth_client, notification):
        response = auth_client.post(
            MARK_READ_URL,
            {"notification_ids": [notification.id]},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["marked_read"] == 1
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_mark_all_as_read(self, auth_client, user, order):
        Notification.objects.create(
            user=user, notification_type="order_created",
            title="A", message="a", order=order,
        )
        Notification.objects.create(
            user=user, notification_type="order_completed",
            title="B", message="b", order=order,
        )
        response = auth_client.post(MARK_READ_URL, {}, format="json")
        assert response.status_code == 200
        assert response.data["marked_read"] == 2
        assert Notification.objects.filter(user=user, is_read=False).count() == 0

    def test_mark_already_read_returns_zero(self, auth_client, notification):
        notification.is_read = True
        notification.save()
        response = auth_client.post(
            MARK_READ_URL,
            {"notification_ids": [notification.id]},
            format="json",
        )
        assert response.data["marked_read"] == 0

    def test_unauthenticated(self, api_client):
        response = api_client.post(MARK_READ_URL, {}, format="json")
        assert response.status_code == 401


@pytest.mark.django_db
class TestUnreadCount:
    def test_unread_count(self, auth_client, notification):
        response = auth_client.get(UNREAD_COUNT_URL)
        assert response.status_code == 200
        assert response.data["unread_count"] == 1

    def test_unread_count_zero(self, auth_client, notification):
        notification.is_read = True
        notification.save()
        response = auth_client.get(UNREAD_COUNT_URL)
        assert response.data["unread_count"] == 0

    def test_unauthenticated(self, api_client):
        response = api_client.get(UNREAD_COUNT_URL)
        assert response.status_code == 401


@pytest.mark.django_db
class TestSendOrderNotificationTask:
    def test_creates_notification(self, user, order):
        send_order_notification(order.id, "order_completed")
        n = Notification.objects.get(order=order, notification_type="order_completed")
        assert n.user == user
        assert order.order_number in n.message

    def test_unknown_type_no_crash(self, order):
        send_order_notification(order.id, "nonexistent_type")
        assert Notification.objects.filter(order=order).count() == 0

    def test_missing_order_no_crash(self):
        send_order_notification(999999, "order_completed")
        assert Notification.objects.count() == 0


@pytest.mark.django_db
class TestNotificationModel:
    def test_str(self, notification, user):
        assert user.email in str(notification)

    def test_default_is_read_false(self, notification):
        assert notification.is_read is False

    def test_ordering(self, user, order):
        n1 = Notification.objects.create(
            user=user, notification_type="order_created",
            title="First", message="first", order=order,
        )
        n2 = Notification.objects.create(
            user=user, notification_type="order_completed",
            title="Second", message="second", order=order,
        )
        notifications = list(Notification.objects.filter(user=user))
        assert notifications[0].id == n2.id  # newest first

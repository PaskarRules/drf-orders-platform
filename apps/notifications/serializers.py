from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id", "notification_type", "title", "message",
            "is_read", "order", "created_at",
        )
        read_only_fields = (
            "id", "notification_type", "title", "message",
            "order", "created_at",
        )


class MarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of notification IDs. If empty, marks all as read.",
    )

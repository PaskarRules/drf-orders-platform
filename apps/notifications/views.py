from django.db import models
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer, MarkReadSerializer


class NotificationListView(generics.ListAPIView):
    """List notifications for the authenticated user, newest first."""
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> models.QuerySet:
        qs = Notification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == "true")
        return qs


class NotificationMarkReadView(APIView):
    """Mark notifications as read — specific IDs or all at once."""
    permission_classes = (IsAuthenticated,)

    def post(self, request) -> Response:
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data.get("notification_ids")

        qs = Notification.objects.filter(user=request.user, is_read=False)
        if ids:
            qs = qs.filter(id__in=ids)

        updated = qs.update(is_read=True)
        return Response({"marked_read": updated}, status=status.HTTP_200_OK)


class UnreadCountView(APIView):
    """Return the count of unread notifications."""
    permission_classes = (IsAuthenticated,)

    def get(self, request) -> Response:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count})

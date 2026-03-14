from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from .models import DailyOrderReport
from .serializers import DailyOrderReportSerializer


class DailyOrderReportListView(generics.ListAPIView):
    queryset = DailyOrderReport.objects.all()
    serializer_class = DailyOrderReportSerializer
    permission_classes = (IsAdminUser,)

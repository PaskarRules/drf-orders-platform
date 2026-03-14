from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.OrderListCreateView.as_view(), name="order-list-create"),
    path("<str:order_number>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("<str:order_number>/cancel/", views.OrderCancelView.as_view(), name="order-cancel"),
]

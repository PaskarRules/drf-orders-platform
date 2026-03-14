from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "products"

router = DefaultRouter()
router.register("products", views.ProductViewSet)
router.register("categories", views.CategoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

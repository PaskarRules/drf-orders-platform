from rest_framework.exceptions import APIException
from rest_framework import status


class InsufficientStockError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Insufficient stock for one or more products."
    default_code = "insufficient_stock"

    def __init__(self, product_name: str, available: int):
        detail = f"Insufficient stock for '{product_name}'. Available: {available}."
        super().__init__(detail=detail)


class InvalidOrderStateError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Order cannot be modified in its current state."
    default_code = "invalid_order_state"

    def __init__(self, order_number: str, current_status: str):
        detail = f"Order {order_number} cannot be modified (status: {current_status})."
        super().__init__(detail=detail)


class ProductNotFoundError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Product not found or inactive."
    default_code = "product_not_found"


class EmptyOrderError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "At least one item is required."
    default_code = "empty_order"

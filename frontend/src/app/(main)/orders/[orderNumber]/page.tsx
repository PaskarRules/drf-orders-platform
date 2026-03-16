"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Order } from "@/lib/types";
import { apiFetch, ApiError } from "@/lib/api-client";
import { API_ROUTES, ROUTES } from "@/lib/constants";
import { formatCurrency, formatDate } from "@/lib/utils";
import { ProtectedRoute } from "@/components/protected-route";
import { OrderStatusBadge } from "@/components/order-status-badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Modal } from "@/components/ui/modal";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

export default function OrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { showToast } = useToast();
  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  useEffect(() => {
    async function fetchOrder() {
      try {
        const data = await apiFetch<Order>(
          `${API_ROUTES.ORDERS}${params.orderNumber}/`
        );
        setOrder(data);
      } catch {
        setOrder(null);
      } finally {
        setIsLoading(false);
      }
    }
    fetchOrder();
  }, [params.orderNumber]);

  const handleCancel = async () => {
    setIsCancelling(true);
    try {
      await apiFetch(`${API_ROUTES.ORDERS}${params.orderNumber}/cancel/`, {
        method: "POST",
      });
      setOrder((prev) => (prev ? { ...prev, status: "cancelled" } : null));
      setShowCancelModal(false);
      showToast("Order cancelled successfully", "success");
    } catch (err) {
      showToast(
        err instanceof ApiError ? err.message : "Failed to cancel order",
        "error"
      );
    } finally {
      setIsCancelling(false);
    }
  };

  const isCancellable =
    order?.status === "pending" || order?.status === "processing";

  return (
    <ProtectedRoute>
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : !order ? (
        <div className="py-12 text-center">
          <h2 className="text-xl font-semibold text-gray-900">Order not found</h2>
          <Button variant="secondary" className="mt-4" onClick={() => router.push(ROUTES.ORDERS)}>
            Back to Orders
          </Button>
        </div>
      ) : (
        <div>
          <button
            onClick={() => router.push(ROUTES.ORDERS)}
            className="mb-6 text-sm text-gray-500 hover:text-gray-700"
          >
            &larr; Back to orders
          </button>

          <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{order.order_number}</h1>
              <p className="text-sm text-gray-500">{formatDate(order.created_at)}</p>
            </div>
            <div className="flex items-center gap-4">
              <OrderStatusBadge status={order.status} />
              {isCancellable && (
                <Button variant="danger" size="sm" onClick={() => setShowCancelModal(true)}>
                  Cancel Order
                </Button>
              )}
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <Card>
                <h2 className="mb-4 text-lg font-semibold">Items</h2>
                <div className="divide-y divide-gray-100">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex items-center justify-between py-3">
                      <div>
                        <p className="font-medium text-gray-900">{item.product_name}</p>
                        <p className="text-sm text-gray-500">
                          {formatCurrency(item.unit_price)} x {item.quantity}
                        </p>
                      </div>
                      <span className="font-medium">{formatCurrency(item.line_total)}</span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            <div>
              <Card>
                <h2 className="mb-4 text-lg font-semibold">Summary</h2>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status</span>
                    <OrderStatusBadge status={order.status} />
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Items</span>
                    <span>{order.items.length}</span>
                  </div>
                  <div className="flex justify-between border-t border-gray-200 pt-2 text-base font-semibold">
                    <span>Total</span>
                    <span>{formatCurrency(order.total_amount)}</span>
                  </div>
                </div>
                {order.notes && (
                  <div className="mt-4 border-t border-gray-200 pt-4">
                    <p className="text-sm font-medium text-gray-700">Notes</p>
                    <p className="mt-1 text-sm text-gray-500">{order.notes}</p>
                  </div>
                )}
              </Card>
            </div>
          </div>

          <Modal
            isOpen={showCancelModal}
            onClose={() => setShowCancelModal(false)}
            title="Cancel Order"
            onConfirm={handleCancel}
            confirmText="Cancel Order"
            confirmVariant="danger"
            isLoading={isCancelling}
          >
            Are you sure you want to cancel order{" "}
            <strong>{order.order_number}</strong>? This action cannot be undone.
          </Modal>
        </div>
      )}
    </ProtectedRoute>
  );
}

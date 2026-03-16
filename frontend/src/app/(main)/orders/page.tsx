"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Order, PaginatedResponse } from "@/lib/types";
import { apiFetch } from "@/lib/api-client";
import { API_ROUTES, ROUTES } from "@/lib/constants";
import { formatCurrency, formatDate } from "@/lib/utils";
import { ProtectedRoute } from "@/components/protected-route";
import { OrderStatusBadge } from "@/components/order-status-badge";
import { Pagination } from "@/components/ui/pagination";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

const PAGE_SIZE = 20;

export default function OrdersPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentPage = parseInt(searchParams.get("page") || "1", 10);

  const fetchOrders = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", currentPage.toString());
      const data = await apiFetch<PaginatedResponse<Order>>(
        `${API_ROUTES.ORDERS}?${params.toString()}`
      );
      setError(null);
      setOrders(data.results);
      setTotalCount(data.count);
    } catch {
      setOrders([]);
      setError("Failed to load orders. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [currentPage]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  return (
    <ProtectedRoute>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">My Orders</h1>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : error ? (
        <div className="py-12 text-center">
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => fetchOrders()}
            className="mt-4 text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Try again
          </button>
        </div>
      ) : orders.length === 0 ? (
        <div className="py-12 text-center text-gray-500">
          <p>No orders yet.</p>
          <Link href={ROUTES.PRODUCTS} className="mt-2 text-sm font-medium text-blue-600">
            Browse Products
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Link key={order.id} href={`${ROUTES.ORDERS}/${order.order_number}`}>
              <Card className="transition-shadow hover:shadow-md">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <h3 className="font-semibold text-gray-900">{order.order_number}</h3>
                    <p className="text-sm text-gray-500">{formatDate(order.created_at)}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600">
                      {order.items.length} item{order.items.length !== 1 ? "s" : ""}
                    </span>
                    <span className="font-semibold">{formatCurrency(order.total_amount)}</span>
                    <OrderStatusBadge status={order.status} />
                  </div>
                </div>
              </Card>
            </Link>
          ))}
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={(page) => router.push(`${ROUTES.ORDERS}?page=${page}`)}
          />
        </div>
      )}
    </ProtectedRoute>
  );
}

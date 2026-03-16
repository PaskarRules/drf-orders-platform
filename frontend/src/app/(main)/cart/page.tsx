"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCart } from "@/hooks/use-cart";
import { apiFetch, ApiError } from "@/lib/api-client";
import { API_ROUTES, ROUTES } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";
import { Order, CreateOrderData } from "@/lib/types";
import { ProtectedRoute } from "@/components/protected-route";
import { CartItem } from "@/components/cart-item";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

export default function CartPage() {
  const { items, total, clearCart } = useCart();
  const router = useRouter();
  const { showToast } = useToast();
  const [notes, setNotes] = useState("");
  const [isPlacing, setIsPlacing] = useState(false);
  const [error, setError] = useState("");

  const handlePlaceOrder = async () => {
    setError("");
    setIsPlacing(true);
    try {
      const orderData: CreateOrderData = {
        items: items.map((item) => ({
          product_id: item.product.id,
          quantity: item.quantity,
        })),
        notes: notes || undefined,
      };
      const order = await apiFetch<Order>(API_ROUTES.ORDERS, {
        method: "POST",
        body: JSON.stringify(orderData),
      });
      clearCart();
      showToast("Order placed successfully!", "success");
      router.push(`${ROUTES.ORDERS}/${order.order_number}`);
    } catch (err) {
      if (err instanceof ApiError) {
        const messages: string[] = [];
        for (const [key, value] of Object.entries(err.data)) {
          if (key === "detail") {
            messages.push(value as string);
          } else if (Array.isArray(value)) {
            messages.push(...value.map(String));
          } else if (typeof value === "string") {
            messages.push(value);
          }
        }
        setError(messages.join(" ") || err.message);
      } else {
        setError("Failed to place order. Please try again.");
      }
    } finally {
      setIsPlacing(false);
    }
  };

  return (
    <ProtectedRoute>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Shopping Cart</h1>

      {items.length === 0 ? (
        <div className="py-12 text-center">
          <p className="text-gray-500">Your cart is empty.</p>
          <Button
            variant="secondary"
            className="mt-4"
            onClick={() => router.push(ROUTES.PRODUCTS)}
          >
            Browse Products
          </Button>
        </div>
      ) : (
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <Card>
              {items.map((item) => (
                <CartItem key={item.product.id} item={item} />
              ))}
            </Card>
          </div>

          <div>
            <Card>
              <h2 className="mb-4 text-lg font-semibold">Order Summary</h2>
              <div className="mb-4 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">
                    Items ({items.reduce((s, i) => s + i.quantity, 0)})
                  </span>
                  <span className="font-medium">{formatCurrency(total)}</span>
                </div>
              </div>
              <div className="mb-4 border-t border-gray-200 pt-4">
                <div className="flex justify-between text-lg font-semibold">
                  <span>Total</span>
                  <span>{formatCurrency(total)}</span>
                </div>
              </div>
              <div className="mb-4">
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Order Notes (optional)
                </label>
                <textarea
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Any special instructions..."
                />
              </div>
              {error && (
                <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-600">
                  {error}
                </div>
              )}
              <Button
                className="w-full"
                size="lg"
                onClick={handlePlaceOrder}
                isLoading={isPlacing}
              >
                Place Order
              </Button>
            </Card>
          </div>
        </div>
      )}
    </ProtectedRoute>
  );
}

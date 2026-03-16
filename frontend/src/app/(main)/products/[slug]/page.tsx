"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Product } from "@/lib/types";
import { apiFetch } from "@/lib/api-client";
import { API_ROUTES, ROUTES } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";
import { useCart } from "@/hooks/use-cart";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { addItem } = useCart();
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    async function fetchProduct() {
      try {
        const data = await apiFetch<Product>(
          `${API_ROUTES.PRODUCTS}${params.slug}/`,
          {},
          false
        );
        setProduct(data);
      } catch {
        setProduct(null);
      } finally {
        setIsLoading(false);
      }
    }
    fetchProduct();
  }, [params.slug]);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="py-12 text-center">
        <h2 className="text-xl font-semibold text-gray-900">Product not found</h2>
        <Button variant="secondary" className="mt-4" onClick={() => router.push(ROUTES.PRODUCTS)}>
          Back to Products
        </Button>
      </div>
    );
  }

  const inStock = product.stock_quantity > 0;

  return (
    <div>
      <button
        onClick={() => router.back()}
        className="mb-6 text-sm text-gray-500 hover:text-gray-700"
        aria-label="Back to products"
      >
        &larr; Back to products
      </button>

      <Card className="grid gap-8 md:grid-cols-2">
        <div className="flex aspect-square items-center justify-center rounded-lg bg-gray-100 text-gray-400">
          <svg className="h-24 w-24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
            />
          </svg>
        </div>

        <div>
          <Badge variant={inStock ? "success" : "danger"} className="mb-3">
            {inStock ? `${product.stock_quantity} in stock` : "Out of stock"}
          </Badge>
          <h1 className="mb-2 text-2xl font-bold text-gray-900">{product.name}</h1>
          <p className="mb-1 text-sm text-gray-500">
            {product.category_name} &middot; SKU: {product.sku}
          </p>
          <p className="mb-6 text-3xl font-bold text-gray-900">
            {formatCurrency(product.price)}
          </p>
          <p className="mb-8 text-gray-600">{product.description}</p>

          {isAuthenticated && inStock && (
            <div className="flex items-center gap-4">
              <div className="flex items-center rounded-md border border-gray-300">
                <button
                  className="px-4 py-2 text-gray-600 hover:bg-gray-50"
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  aria-label="Decrease quantity"
                >
                  -
                </button>
                <span className="min-w-[3rem] border-x border-gray-300 px-4 py-2 text-center">
                  {quantity}
                </span>
                <button
                  className="px-4 py-2 text-gray-600 hover:bg-gray-50"
                  onClick={() =>
                    setQuantity(Math.min(product.stock_quantity, quantity + 1))
                  }
                  aria-label="Increase quantity"
                >
                  +
                </button>
              </div>
              <Button
                size="lg"
                onClick={() => {
                  addItem(product, quantity);
                  showToast(`${quantity}x ${product.name} added to cart`, "success");
                }}
              >
                Add to Cart
              </Button>
            </div>
          )}

          {!isAuthenticated && (
            <p className="text-sm text-gray-500">
              <button
                onClick={() => router.push(ROUTES.LOGIN)}
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Sign in
              </button>{" "}
              to add items to your cart.
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}

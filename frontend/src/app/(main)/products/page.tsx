"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Product, PaginatedResponse } from "@/lib/types";
import { apiFetch } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import { ProductCard } from "@/components/product-card";
import { ProductFilters } from "@/components/product-filters";
import { Pagination } from "@/components/ui/pagination";
import { Spinner } from "@/components/ui/spinner";

const PAGE_SIZE = 20;

export default function ProductsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentPage = parseInt(searchParams.get("page") || "1", 10);
  const filters = {
    search: searchParams.get("search") || "",
    category: searchParams.get("category") || "",
    min_price: searchParams.get("min_price") || "",
    max_price: searchParams.get("max_price") || "",
    in_stock: searchParams.get("in_stock") || "",
    ordering: searchParams.get("ordering") || "",
  };

  const fetchProducts = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", currentPage.toString());
      if (filters.search) params.set("search", filters.search);
      if (filters.category) params.set("category", filters.category);
      if (filters.min_price) params.set("min_price", filters.min_price);
      if (filters.max_price) params.set("max_price", filters.max_price);
      if (filters.in_stock) params.set("in_stock", filters.in_stock);
      if (filters.ordering) params.set("ordering", filters.ordering);

      const data = await apiFetch<PaginatedResponse<Product>>(
        `${API_ROUTES.PRODUCTS}?${params.toString()}`,
        {},
        false
      );
      setError(null);
      setProducts(data.results);
      setTotalCount(data.count);
    } catch {
      setProducts([]);
      setError("Failed to load products. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, filters.search, filters.category, filters.min_price, filters.max_price, filters.in_stock, filters.ordering]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const updateURL = useCallback(
    (newFilters: typeof filters, page = 1) => {
      const params = new URLSearchParams();
      if (page > 1) params.set("page", page.toString());
      Object.entries(newFilters).forEach(([key, value]) => {
        if (value) params.set(key, value);
      });
      router.push(`/products?${params.toString()}`);
    },
    [router]
  );

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Products</h1>
        <p className="mt-1 text-sm text-gray-500">{totalCount} products found</p>
      </div>

      <ProductFilters
        filters={filters}
        onFiltersChange={(newFilters) => updateURL(newFilters)}
      />

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : error ? (
        <div className="py-12 text-center">
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => fetchProducts()}
            className="mt-4 text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Try again
          </button>
        </div>
      ) : products.length === 0 ? (
        <div className="py-12 text-center text-gray-500">
          No products found. Try adjusting your filters.
        </div>
      ) : (
        <>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={(page) => updateURL(filters, page)}
          />
        </>
      )}
    </div>
  );
}

"use client";

import Link from "next/link";
import { Product } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";
import { useCart } from "@/hooks/use-cart";
import { useAuth } from "@/hooks/use-auth";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { useToast } from "./ui/toast";

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const { addItem } = useCart();
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const inStock = product.stock_quantity > 0;

  return (
    <Card className="flex flex-col justify-between transition-shadow hover:shadow-md">
      <div>
        <Link href={`/products/${product.slug}`}>
          <h3 className="mb-1 text-base font-semibold text-gray-900 hover:text-blue-600">
            {product.name}
          </h3>
        </Link>
        <p className="mb-2 text-xs text-gray-500">{product.category_name}</p>
        <p className="mb-3 line-clamp-2 text-sm text-gray-600">{product.description}</p>
        <div className="mb-3 flex items-center justify-between">
          <span className="text-lg font-bold text-gray-900">{formatCurrency(product.price)}</span>
          <Badge variant={inStock ? "success" : "danger"}>
            {inStock ? `${product.stock_quantity} in stock` : "Out of stock"}
          </Badge>
        </div>
      </div>
      {isAuthenticated && (
        <Button
          size="sm"
          className="w-full"
          disabled={!inStock}
          onClick={() => {
            addItem(product);
            showToast(`${product.name} added to cart`, "success");
          }}
        >
          {inStock ? "Add to Cart" : "Out of Stock"}
        </Button>
      )}
    </Card>
  );
}

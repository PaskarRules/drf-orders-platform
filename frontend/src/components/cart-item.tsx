"use client";

import { CartItem as CartItemType } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";
import { useCart } from "@/hooks/use-cart";
import { Button } from "./ui/button";

interface CartItemProps {
  item: CartItemType;
}

export function CartItem({ item }: CartItemProps) {
  const { updateQuantity, removeItem } = useCart();
  const { product, quantity } = item;
  const lineTotal = parseFloat(product.price) * quantity;

  return (
    <div className="flex items-center justify-between border-b border-gray-100 py-4">
      <div className="flex-1">
        <h4 className="font-medium text-gray-900">{product.name}</h4>
        <p className="text-sm text-gray-500">
          {formatCurrency(product.price)} each
        </p>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center rounded-md border border-gray-300">
          <button
            className="px-3 py-1 text-gray-600 hover:bg-gray-50"
            onClick={() => updateQuantity(product.id, quantity - 1)}
            aria-label="Decrease quantity"
          >
            -
          </button>
          <span className="min-w-[2rem] border-x border-gray-300 px-3 py-1 text-center text-sm">
            {quantity}
          </span>
          <button
            className="px-3 py-1 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
            onClick={() => updateQuantity(product.id, quantity + 1)}
            disabled={quantity >= product.stock_quantity}
            aria-label="Increase quantity"
          >
            +
          </button>
        </div>
        <span className="w-24 text-right font-medium">{formatCurrency(lineTotal)}</span>
        <Button variant="ghost" size="sm" onClick={() => removeItem(product.id)} aria-label="Remove item">
          <svg className="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </Button>
      </div>
    </div>
  );
}

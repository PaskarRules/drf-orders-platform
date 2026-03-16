"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Category } from "@/lib/types";
import { apiFetch } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import { Input } from "./ui/input";
import { Select } from "./ui/select";
import { Button } from "./ui/button";

interface ProductFilters {
  search: string;
  category: string;
  min_price: string;
  max_price: string;
  in_stock: string;
  ordering: string;
}

interface ProductFiltersProps {
  filters: ProductFilters;
  onFiltersChange: (filters: ProductFilters) => void;
}

export function ProductFilters({ filters, onFiltersChange }: ProductFiltersProps) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [searchInput, setSearchInput] = useState(filters.search);
  const filtersRef = useRef(filters);
  const onChangeRef = useRef(onFiltersChange);
  filtersRef.current = filters;
  onChangeRef.current = onFiltersChange;

  useEffect(() => {
    apiFetch<{ results: Category[] }>(API_ROUTES.CATEGORIES, {}, false)
      .then((data) => setCategories(data.results || []))
      .catch(() => {});
  }, []);

  // Debounced search
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (searchInput !== filtersRef.current.search) {
        onChangeRef.current({ ...filtersRef.current, search: searchInput });
      }
    }, 400);
    return () => clearTimeout(timeout);
  }, [searchInput]);

  const updateFilter = useCallback(
    (key: keyof ProductFilters, value: string) => {
      onFiltersChange({ ...filters, [key]: value });
    },
    [filters, onFiltersChange]
  );

  const clearFilters = () => {
    setSearchInput("");
    onFiltersChange({
      search: "",
      category: "",
      min_price: "",
      max_price: "",
      in_stock: "",
      ordering: "",
    });
  };

  const categoryOptions = [
    { value: "", label: "All Categories" },
    ...categories.map((c) => ({ value: c.slug, label: c.name })),
  ];

  const orderingOptions = [
    { value: "", label: "Default" },
    { value: "name", label: "Name A-Z" },
    { value: "-name", label: "Name Z-A" },
    { value: "price", label: "Price: Low to High" },
    { value: "-price", label: "Price: High to Low" },
    { value: "-created_at", label: "Newest First" },
  ];

  const stockOptions = [
    { value: "", label: "All" },
    { value: "true", label: "In Stock" },
    { value: "false", label: "Out of Stock" },
  ];

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
        <div className="lg:col-span-2">
          <Input
            placeholder="Search products..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
        </div>
        <Select
          options={categoryOptions}
          value={filters.category}
          onChange={(e) => updateFilter("category", e.target.value)}
        />
        <Input
          type="number"
          placeholder="Min price"
          value={filters.min_price}
          onChange={(e) => updateFilter("min_price", e.target.value)}
        />
        <Input
          type="number"
          placeholder="Max price"
          value={filters.max_price}
          onChange={(e) => updateFilter("max_price", e.target.value)}
        />
        <div className="flex gap-2">
          <Select
            options={stockOptions}
            value={filters.in_stock}
            onChange={(e) => updateFilter("in_stock", e.target.value)}
          />
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <Select
          options={orderingOptions}
          value={filters.ordering}
          onChange={(e) => updateFilter("ordering", e.target.value)}
          className="w-48"
        />
        <Button variant="ghost" size="sm" onClick={clearFilters}>
          Clear Filters
        </Button>
      </div>
    </div>
  );
}

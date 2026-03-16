"use client";

import { useAuth } from "@/hooks/use-auth";
import { ROUTES } from "@/lib/constants";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Spinner } from "./ui/spinner";

export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push(ROUTES.LOGIN);
      } else if (!user?.is_staff) {
        router.push(ROUTES.PRODUCTS);
      }
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated || !user?.is_staff) return null;

  return <>{children}</>;
}

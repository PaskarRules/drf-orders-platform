"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ROUTES } from "@/lib/constants";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.replace(ROUTES.PRODUCTS);
  }, [router]);
  return null;
}

"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import { useAuth } from "./use-auth";

export function useNotifications() {
  const { isAuthenticated } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchUnreadCount = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const data = await apiFetch<{ unread_count: number }>(
        API_ROUTES.NOTIFICATIONS_UNREAD_COUNT
      );
      setUnreadCount(data.unread_count);
    } catch {
      // Silently fail for notification polling
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) return;
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 60000);
    return () => clearInterval(interval);
  }, [fetchUnreadCount, isAuthenticated]);

  return { unreadCount, refreshCount: fetchUnreadCount };
}

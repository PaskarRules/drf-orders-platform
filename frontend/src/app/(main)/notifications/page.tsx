"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Notification, PaginatedResponse } from "@/lib/types";
import { apiFetch } from "@/lib/api-client";
import { API_ROUTES, ROUTES } from "@/lib/constants";
import { ProtectedRoute } from "@/components/protected-route";
import { NotificationItem } from "@/components/notification-item";
import { Button } from "@/components/ui/button";
import { Pagination } from "@/components/ui/pagination";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

const PAGE_SIZE = 20;

export default function NotificationsPage() {
  const { showToast } = useToast();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  const currentPage = parseInt(searchParams.get("page") || "1", 10);

  const fetchNotifications = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", currentPage.toString());
      const data = await apiFetch<PaginatedResponse<Notification>>(
        `${API_ROUTES.NOTIFICATIONS}?${params.toString()}`
      );
      setNotifications(data.results);
      setTotalCount(data.count);
    } catch {
      setNotifications([]);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const markAllRead = async () => {
    try {
      await apiFetch(API_ROUTES.NOTIFICATIONS_MARK_READ, {
        method: "POST",
        body: JSON.stringify({}),
      });
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      showToast("All notifications marked as read", "success");
    } catch {
      showToast("Failed to mark notifications as read", "error");
    }
  };

  const markOneRead = async (id: number) => {
    try {
      await apiFetch(API_ROUTES.NOTIFICATIONS_MARK_READ, {
        method: "POST",
        body: JSON.stringify({ notification_ids: [id] }),
      });
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch {
      showToast("Failed to mark notification as read", "error");
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;
  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  return (
    <ProtectedRoute>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          {unreadCount > 0 && (
            <p className="text-sm text-gray-500">{unreadCount} unread</p>
          )}
        </div>
        {unreadCount > 0 && (
          <Button variant="secondary" size="sm" onClick={markAllRead}>
            Mark all as read
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : notifications.length === 0 ? (
        <div className="py-12 text-center text-gray-500">No notifications yet.</div>
      ) : (
        <div className="space-y-3">
          {notifications.map((notification) => (
            <div
              key={notification.id}
              onClick={() => {
                if (!notification.is_read) markOneRead(notification.id);
              }}
              className="cursor-pointer"
            >
              <NotificationItem notification={notification} />
            </div>
          ))}
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={(page) => router.push(`${ROUTES.NOTIFICATIONS}?page=${page}`)}
          />
        </div>
      )}
    </ProtectedRoute>
  );
}

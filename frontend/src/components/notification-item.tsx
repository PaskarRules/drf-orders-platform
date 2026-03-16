"use client";

import { Notification } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface NotificationItemProps {
  notification: Notification;
}

export function NotificationItem({ notification }: NotificationItemProps) {
  return (
    <div
      className={cn(
        "rounded-md border p-4",
        notification.is_read
          ? "border-gray-200 bg-white"
          : "border-blue-200 bg-blue-50"
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <h4 className="font-medium text-gray-900">{notification.title}</h4>
          <p className="mt-1 text-sm text-gray-600">{notification.message}</p>
        </div>
        {!notification.is_read && (
          <span className="mt-1 h-2 w-2 flex-shrink-0 rounded-full bg-blue-600" />
        )}
      </div>
      <p className="mt-2 text-xs text-gray-400">{formatDate(notification.created_at)}</p>
    </div>
  );
}

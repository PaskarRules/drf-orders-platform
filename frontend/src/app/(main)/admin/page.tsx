"use client";

import { useCallback, useEffect, useState } from "react";
import { DailyOrderReport, PaginatedResponse } from "@/lib/types";
import { apiFetch } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";
import { AdminRoute } from "@/components/admin-route";
import { ReportChart } from "@/components/report-chart";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

export default function AdminPage() {
  const [reports, setReports] = useState<DailyOrderReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchReports = useCallback(async () => {
    try {
      const data = await apiFetch<PaginatedResponse<DailyOrderReport>>(
        API_ROUTES.REPORTS_DAILY
      );
      setReports(data.results);
    } catch {
      setReports([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const totalRevenue = reports.reduce(
    (sum, r) => sum + parseFloat(r.total_revenue),
    0
  );
  const totalOrders = reports.reduce((sum, r) => sum + r.total_orders, 0);
  const avgOrderValue =
    totalOrders > 0 ? totalRevenue / totalOrders : 0;

  return (
    <AdminRoute>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Admin Dashboard</h1>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <>
          <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <p className="text-sm text-gray-500">Total Revenue</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">
                {formatCurrency(totalRevenue)}
              </p>
            </Card>
            <Card>
              <p className="text-sm text-gray-500">Total Orders</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{totalOrders}</p>
            </Card>
            <Card>
              <p className="text-sm text-gray-500">Avg Order Value</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">
                {formatCurrency(avgOrderValue)}
              </p>
            </Card>
            <Card>
              <p className="text-sm text-gray-500">Reports</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{reports.length}</p>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Daily Reports</CardTitle>
            </CardHeader>
            <CardContent>
              <ReportChart reports={reports} />
            </CardContent>
          </Card>
        </>
      )}
    </AdminRoute>
  );
}

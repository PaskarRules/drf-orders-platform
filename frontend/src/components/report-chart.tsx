"use client";

import { DailyOrderReport } from "@/lib/types";
import { formatCurrency, formatShortDate } from "@/lib/utils";

interface ReportChartProps {
  reports: DailyOrderReport[];
}

export function ReportChart({ reports }: ReportChartProps) {
  if (reports.length === 0) {
    return <p className="text-sm text-gray-500">No report data available.</p>;
  }

  const maxRevenue = Math.max(...reports.map((r) => parseFloat(r.total_revenue)));
  const sortedReports = [...reports].sort(
    (a, b) => new Date(a.report_date).getTime() - new Date(b.report_date).getTime()
  );

  return (
    <div className="space-y-6">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500">
              <th className="pb-2 pr-4 font-medium">Date</th>
              <th className="pb-2 pr-4 font-medium">Orders</th>
              <th className="pb-2 pr-4 font-medium">Revenue</th>
              <th className="pb-2 pr-4 font-medium">Avg Value</th>
              <th className="pb-2 pr-4 font-medium">Completed</th>
              <th className="pb-2 pr-4 font-medium">Failed</th>
              <th className="pb-2 pr-4 font-medium">Cancelled</th>
              <th className="pb-2 font-medium">Revenue Bar</th>
            </tr>
          </thead>
          <tbody>
            {sortedReports.map((report) => (
              <tr key={report.id} className="border-b border-gray-100">
                <td className="py-2 pr-4 font-medium">{formatShortDate(report.report_date)}</td>
                <td className="py-2 pr-4">{report.total_orders}</td>
                <td className="py-2 pr-4">{formatCurrency(report.total_revenue)}</td>
                <td className="py-2 pr-4">{formatCurrency(report.avg_order_value)}</td>
                <td className="py-2 pr-4 text-green-600">{report.completed_count}</td>
                <td className="py-2 pr-4 text-red-600">{report.failed_count}</td>
                <td className="py-2 pr-4 text-gray-500">{report.cancelled_count}</td>
                <td className="py-2">
                  <div className="h-4 w-full rounded-full bg-gray-100">
                    <div
                      className="h-4 rounded-full bg-blue-500"
                      style={{
                        width: `${maxRevenue > 0 ? (parseFloat(report.total_revenue) / maxRevenue) * 100 : 0}%`,
                      }}
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

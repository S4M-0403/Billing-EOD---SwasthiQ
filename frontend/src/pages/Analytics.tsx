import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import type {
  EODReport,
} from "../types/report";

export default function Analytics({
  report,
}: {
  report: EODReport | null;
}) {
  if (!report) {
    return (
      <p className="text-slate-500">
        Upload a billing log first.
      </p>
    );
  }

  const analytics = report.analytics;

  const chartData =
    analytics.revenue_by_hour.map(
      (item) => ({
        hour: `${item.hour}:00`,
        revenue:
          item.revenue_paise / 100,
      })
    );

  return (
    <div>
      <h2 className="text-3xl font-bold">
        Analytics
      </h2>

      <p className="text-slate-500 mb-8">
        Revenue and medicine performance
      </p>

      <div className="bg-white border rounded-xl p-6 mb-8">
        <div className="flex justify-between mb-5">
          <h3 className="font-semibold">
            Revenue by Hour
          </h3>

          <span className="text-sm">
            Peak:{" "}
            <strong>
              {analytics.peak_hour !== null
                ? `${analytics.peak_hour}:00`
                : "N/A"}
            </strong>
          </span>
        </div>

        <div className="h-80">
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <BarChart data={chartData}>
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="revenue" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Ranking
          title="Top Medicines by Quantity"
          items={analytics.top_medicines_by_quantity.map(
            (item) => ({
              name: item.drug_name,
              value: `${item.quantity} units`,
            })
          )}
        />

        <Ranking
          title="Top Medicines by Revenue"
          items={analytics.top_medicines_by_revenue.map(
            (item) => ({
              name: item.drug_name,
              value: `₹${(
                item.revenue_paise / 100
              ).toLocaleString("en-IN")}`,
            })
          )}
        />
      </div>
    </div>
  );
}

function Ranking({
  title,
  items,
}: {
  title: string;
  items: {
    name: string;
    value: string;
  }[];
}) {
  return (
    <div className="bg-white border rounded-xl p-6">
      <h3 className="font-semibold mb-4">
        {title}
      </h3>

      <div className="space-y-4">
        {items.map((item, index) => (
          <div
            key={item.name}
            className="flex justify-between border-b pb-3"
          >
            <span>
              {index + 1}. {item.name}
            </span>

            <strong>{item.value}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
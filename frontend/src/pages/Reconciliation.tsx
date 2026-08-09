import { useState } from "react";

import { analyzeBilling } from "../services/api";

import type {
  EODReport,
  Narrative,
} from "../types/report";

interface Props {
  report: EODReport | null;
  setReport: (report: EODReport | null) => void;
  setNarrative: (narrative: Narrative | null) => void;
}

function money(paise: number) {
  return `₹${(paise / 100).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function Reconciliation({
  report,
  setReport,
  setNarrative,
}: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleUpload(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const data = await analyzeBilling(file);

      setReport(data.report);
      setNarrative(data.narrative);
    } catch (error: any) {
      console.error(error);

      setReport(null);
      setNarrative(null);

      const detail = error?.response?.data?.detail;

      if (detail?.message) {
        setError(detail.message);
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError(
          "Unable to analyze the billing file. Please check the file and try again."
        );
      }
    } finally {
      setLoading(false);

      // Allows selecting the same file again after an error.
      event.target.value = "";
    }
  }

  /*
   * Empty state before the first successful upload.
   */
  if (!report) {
    return (
      <div className="max-w-4xl">
        <div className="mb-8">
          <p className="text-sm font-medium text-slate-500 mb-2">
            SWASTHIQ / BILLING
          </p>

          <h2 className="text-3xl font-bold text-slate-900">
            EOD Reconciliation
          </h2>

          <p className="text-slate-500 mt-2">
            Upload a clinic billing log to generate reconciliation,
            analytics, and an AI-powered end-of-day summary.
          </p>
        </div>

        {error && (
          <div className="mb-6 border border-red-200 bg-red-50 rounded-xl p-4">
            <p className="font-semibold text-red-800">
              Analysis failed
            </p>

            <p className="text-sm text-red-700 mt-1">
              {error}
            </p>
          </div>
        )}

        <div className="bg-white border border-dashed border-slate-300 rounded-2xl p-12 text-center">
          <div className="mx-auto mb-5 w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center">
            <span className="text-xl">↑</span>
          </div>

          <h3 className="text-lg font-semibold text-slate-900">
            Upload billing log
          </h3>

          <p className="text-sm text-slate-500 mt-2 mb-6">
            Select a JSON billing log to begin analysis.
          </p>

          <label className="inline-flex items-center justify-center bg-slate-900 text-white px-5 py-3 rounded-lg cursor-pointer hover:bg-slate-800 transition">
            {loading ? "Analyzing..." : "Choose JSON file"}

            <input
              type="file"
              accept=".json,application/json"
              onChange={handleUpload}
              disabled={loading}
              className="hidden"
            />
          </label>

          <p className="text-xs text-slate-400 mt-4">
            JSON files only
          </p>
        </div>
      </div>
    );
  }

  const {
    total_billed_paise,
    total_collected_paise,
    total_outstanding_paise,
    total_refunds_paise,
    by_payment_mode,
  } = report.reconciliation;

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <p className="text-sm font-medium text-slate-500 mb-2">
            SWASTHIQ / BILLING
          </p>

          <h2 className="text-3xl font-bold text-slate-900">
            EOD Reconciliation
          </h2>

          <p className="text-slate-500 mt-2">
            {report.clinic_id} · {report.report_date}
          </p>
        </div>

        <label className="inline-flex items-center bg-slate-900 text-white px-5 py-3 rounded-lg cursor-pointer hover:bg-slate-800 transition">
          {loading ? "Analyzing..." : "Upload Another"}

          <input
            type="file"
            accept=".json,application/json"
            onChange={handleUpload}
            disabled={loading}
            className="hidden"
          />
        </label>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 border border-red-200 bg-red-50 rounded-xl p-4">
          <p className="font-semibold text-red-800">
            Analysis failed
          </p>

          <p className="text-sm text-red-700 mt-1">
            {error}
          </p>
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">
        <Stat
          title="Total Billed"
          value={money(total_billed_paise)}
        />

        <Stat
          title="Collected"
          value={money(total_collected_paise)}
        />

        <Stat
          title="Outstanding"
          value={money(total_outstanding_paise)}
        />

        <Stat
          title="Refunds"
          value={money(total_refunds_paise)}
        />
      </div>

      {/* Payment mode breakdown */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="mb-5">
          <h3 className="text-lg font-semibold text-slate-900">
            Payment Mode Breakdown
          </h3>

          <p className="text-sm text-slate-500 mt-1">
            Reconciliation by payment method.
          </p>
        </div>

        {Object.keys(by_payment_mode).length === 0 ? (
          <div className="py-12 text-center">
            <p className="font-medium text-slate-700">
              No billing transactions
            </p>

            <p className="text-sm text-slate-500 mt-1">
              No payment activity was recorded for this day.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-slate-500 border-b">
                  <th className="pb-3 font-medium">
                    Mode
                  </th>

                  <th className="pb-3 font-medium">
                    Billed
                  </th>

                  <th className="pb-3 font-medium">
                    Collected
                  </th>

                  <th className="pb-3 font-medium">
                    Outstanding
                  </th>

                  <th className="pb-3 font-medium">
                    Refunds
                  </th>
                </tr>
              </thead>

              <tbody>
                {Object.entries(by_payment_mode).map(
                  ([mode, data]) => (
                    <tr
                      key={mode}
                      className="border-b last:border-b-0"
                    >
                      <td className="py-4 font-medium text-slate-800 capitalize">
                        {mode}
                      </td>

                      <td className="py-4 text-slate-700">
                        {money(data.billed_paise)}
                      </td>

                      <td className="py-4 text-slate-700">
                        {money(data.collected_paise)}
                      </td>

                      <td className="py-4 text-slate-700">
                        {money(data.outstanding_paise)}
                      </td>

                      <td className="py-4 text-slate-700">
                        {money(data.refunds_paise)}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Loading overlay */}
      {loading && (
        <div className="fixed inset-0 bg-slate-900/20 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl px-8 py-6 text-center">
            <div className="mx-auto mb-4 w-8 h-8 border-4 border-slate-200 border-t-slate-900 rounded-full animate-spin" />

            <p className="font-semibold text-slate-900">
              Analyzing billing log
            </p>

            <p className="text-sm text-slate-500 mt-1">
              Validating data and generating the report...
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <p className="text-sm text-slate-500">
        {title}
      </p>

      <p className="text-2xl font-bold text-slate-900 mt-2">
        {value}
      </p>
    </div>
  );
}
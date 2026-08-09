import type { Narrative as NarrativeType } from "../types/report";

export default function Narrative({
  narrative,
}: {
  narrative: NarrativeType | null;
}) {
  if (!narrative) {
    return (
      <div>
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-900">
            AI Narrative Summary
          </h2>

          <p className="text-slate-500 mt-2">
            Generated from today's reconciliation.
          </p>
        </div>

        <div className="bg-white border rounded-xl p-10 text-center">
          <p className="font-medium text-slate-700">
            No summary available
          </p>

          <p className="text-sm text-slate-500 mt-2">
            Upload a billing log from the Reconciliation
            page to generate an AI summary.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <h2 className="text-3xl font-bold text-slate-900">
            AI Narrative Summary
          </h2>

          <span className="text-[10px] font-bold tracking-wide bg-purple-100 text-purple-700 px-2 py-1 rounded">
            AI SUGGESTED
          </span>
        </div>

        <p className="text-slate-500 mt-2">
          Generated from today's reconciliation and grounded
          in deterministic billing calculations.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        {/* Narrative */}
        <div className="xl:col-span-3 bg-white border rounded-xl p-8">
          <div className="flex items-center gap-2 mb-6">
            <span className="w-2 h-2 rounded-full bg-green-500" />

            <span className="text-sm font-medium text-green-700">
              Grounded summary
            </span>
          </div>

          <div className="rounded-xl bg-green-50 border border-green-100 p-6">
            <p className="text-[15px] leading-7 text-slate-800 whitespace-pre-line">
              {narrative.narrative}
            </p>
          </div>
        </div>

        {/* Traced figures */}
        <div className="xl:col-span-2 bg-white border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-slate-900">
            Traced Figures
          </h3>

          <p className="text-sm text-slate-500 mt-1 mb-6">
            Every number shown in the summary is mapped back
            to the deterministic report.
          </p>

          {narrative.traced_figures.length === 0 ? (
            <div className="py-8 text-center">
              <p className="text-sm text-slate-500">
                No figures were referenced in this summary.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {narrative.traced_figures.map((figure) => (
                <div
                  key={`${figure.token}-${figure.source}`}
                  className="border border-slate-200 rounded-lg p-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-semibold text-slate-900">
                      {figure.display_value}
                    </span>

                    <span className="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded">
                      grounded
                    </span>
                  </div>

                  <p className="text-xs text-slate-500 mt-2 break-all">
                    {formatSource(figure.source)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


function formatSource(source: string) {
  return source
    .replace("reconciliation.", "")
    .replace("analytics.", "")
    .replace("[peak_hour]", "")
    .replace("[0]", "")
    .replace("_paise", "")
    .replaceAll("_", " ");
}
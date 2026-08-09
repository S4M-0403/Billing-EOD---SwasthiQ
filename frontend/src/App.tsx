import { useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Sidebar from "./components/Sidebar";

import Reconciliation from "./pages/Reconciliation";
import Analytics from "./pages/Analytics";
import Narrative from "./pages/Narrative";

import type {
  EODReport,
  Narrative as NarrativeType,
} from "./types/report";


function App() {
  const [report, setReport] =
    useState<EODReport | null>(null);

  const [narrative, setNarrative] =
    useState<NarrativeType | null>(null);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 flex">
        <Sidebar />

        <main className="flex-1 min-w-0 p-6 md:p-8">
          <Routes>
            <Route
              path="/"
              element={
                <Reconciliation
                  report={report}
                  setReport={setReport}
                  setNarrative={setNarrative}
                />
              }
            />

            <Route
              path="/analytics"
              element={
                <Analytics
                  report={report}
                />
              }
            />

            <Route
              path="/narrative"
              element={
                <Narrative
                  narrative={narrative}
                />
              }
            />

            <Route
              path="*"
              element={
                <Navigate
                  to="/"
                  replace
                />
              }
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
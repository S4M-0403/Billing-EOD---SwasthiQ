import {
  LayoutDashboard,
  BarChart3,
  Sparkles,
} from "lucide-react";
import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const links = [
    {
      to: "/",
      label: "Reconciliation",
      icon: LayoutDashboard,
    },
    {
      to: "/analytics",
      label: "Analytics",
      icon: BarChart3,
    },
    {
      to: "/narrative",
      label: "AI Summary",
      icon: Sparkles,
    },
  ];

  return (
    <aside className="w-64 bg-white border-r min-h-screen p-5">
      <div className="mb-10">
        <h1 className="text-xl font-bold">
          SwasthiQ
        </h1>

        <p className="text-sm text-slate-500">
          EOD Billing Intelligence
        </p>
      </div>

      <nav className="space-y-2">
        {links.map(
          ({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg ${
                  isActive
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          )
        )}
      </nav>
    </aside>
  );
}
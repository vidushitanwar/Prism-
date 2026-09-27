import { NavLink } from "react-router-dom";
import clsx from "clsx";

const NAV_LINKS = [
  { to: "/explore", label: "Explore" },
  { to: "/emerging", label: "Emerging Skills" },
  { to: "/ghost-skills", label: "Ghost Skills" },
  { to: "/radar", label: "Radar" },
  { to: "/structural-shifts", label: "Structural Shifts" },
  { to: "/routes", label: "Navigate" },
  { to: "/simulate", label: "Simulate" },
  { to: "/insights", label: "Insights" },
  { to: "/talent-dna", label: "Talent DNA" },
];

export function AppNav() {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-prism-700/50 bg-prism-950/90 px-4 backdrop-blur-xl">
      <div className="flex items-center gap-6">
        <NavLink to="/" className="font-display text-sm tracking-widest text-prism-100">
          PRISM
        </NavLink>
        <nav className="hidden items-center gap-1 overflow-x-auto sm:flex">
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                clsx(
                  "rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
                  isActive ? "bg-prism-800/80 text-prism-100" : "text-prism-400 hover:text-prism-100"
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="flex items-center gap-2 text-[11px] text-prism-500">
        <kbd className="rounded border border-prism-700 px-1.5 py-0.5">Ctrl</kbd>
        <span>+</span>
        <kbd className="rounded border border-prism-700 px-1.5 py-0.5">K</kbd>
        <span className="ml-1 hidden sm:inline">Command Center</span>
      </div>
    </header>
  );
}

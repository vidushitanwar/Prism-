import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/services/api";
import { useGraphStore } from "@/store/useGraphStore";
import { useKeyboardShortcut } from "@/hooks/useKeyboardShortcut";
import type { SearchResponse } from "@/types/graph";

const STATIC_COMMANDS = [
  { label: "Explore Workforce Map", action: "navigate", target: "/explore" },
  { label: "Show Emerging Skills", action: "navigate", target: "/emerging" },
  { label: "Show Ghost Skills", action: "navigate", target: "/ghost-skills" },
  { label: "Open Workforce Radar", action: "navigate", target: "/radar" },
  { label: "Open Structural Shift Detector", action: "navigate", target: "/structural-shifts" },
  { label: "Open Career Route Planner", action: "navigate", target: "/routes" },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResponse["results"] | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const focusNode = useGraphStore((s) => s.focusNode);

  useKeyboardShortcut("k", () => setOpen((v) => !v), { ctrlOrCmd: true });
  useKeyboardShortcut("Escape", () => setOpen(false));

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 30);
    else {
      setQuery("");
      setResults(null);
    }
  }, [open]);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults(null);
      return;
    }
    const timeout = setTimeout(async () => {
      try {
        const res = await api.search(query.trim());
        setResults(res.results);
      } catch {
        setResults(null);
      }
    }, 200);
    return () => clearTimeout(timeout);
  }, [query]);

  if (!open) return null;

  const dynamicResults = results
    ? [
        ...results.skills.map((r) => ({ label: `Explore skill: ${r.name}`, nodeId: r.node_id })),
        ...results.occupations.map((r) => ({ label: `Explore occupation: ${r.name}`, nodeId: r.node_id })),
        ...results.industries.map((r) => ({ label: `Explore industry: ${r.name}`, nodeId: r.node_id })),
      ]
    : [];

  const filteredStatic = STATIC_COMMANDS.filter((c) =>
    c.label.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 pt-[15vh]" onClick={() => setOpen(false)}>
      <div
        className="w-full max-w-xl overflow-hidden rounded-2xl border border-prism-600/50 bg-prism-900/95 shadow-2xl backdrop-blur-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 border-b border-prism-700/50 px-4 py-3">
          <span className="text-prism-500">⌘K</span>
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search Generative AI, Show emerging skills, Explore Data Scientist…"
            className="flex-1 bg-transparent text-sm text-prism-100 outline-none placeholder:text-prism-500"
          />
          <kbd className="rounded border border-prism-700 px-1.5 py-0.5 text-[10px] text-prism-500">Esc</kbd>
        </div>

        <div className="max-h-80 overflow-y-auto py-2">
          {filteredStatic.map((c) => (
            <button
              key={c.label}
              onClick={() => {
                navigate(c.target);
                setOpen(false);
              }}
              className="flex w-full items-center px-4 py-2.5 text-left text-sm text-prism-200 hover:bg-prism-800/70"
            >
              {c.label}
            </button>
          ))}

          {dynamicResults.length > 0 && (
            <div className="mt-1 border-t border-prism-700/40 pt-1">
              {dynamicResults.map((r) => (
                <button
                  key={r.nodeId}
                  onClick={() => {
                    navigate("/explore");
                    focusNode(r.nodeId);
                    setOpen(false);
                  }}
                  className="flex w-full items-center px-4 py-2.5 text-left text-sm text-prism-200 hover:bg-prism-800/70"
                >
                  {r.label}
                </button>
              ))}
            </div>
          )}

          {filteredStatic.length === 0 && dynamicResults.length === 0 && (
            <p className="px-4 py-4 text-xs text-prism-500">No matches. Try a skill, occupation, or industry name.</p>
          )}
        </div>
      </div>
    </div>
  );
}

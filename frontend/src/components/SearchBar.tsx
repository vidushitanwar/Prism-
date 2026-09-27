import { useState, useRef, useEffect } from "react";
import { api } from "@/services/api";
import { useGraphStore } from "@/store/useGraphStore";
import type { SearchResponse } from "@/types/graph";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResponse["results"] | null>(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const focusNode = useGraphStore((s) => s.focusNode);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults(null);
      return;
    }
    const timeout = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await api.search(query.trim());
        setResults(res.results);
        setOpen(true);
      } catch {
        setResults(null);
      } finally {
        setLoading(false);
      }
    }, 250); // debounced search
    return () => clearTimeout(timeout);
  }, [query]);

  const flatResults = results
    ? [
        ...results.skills.map((r) => ({ ...r, kind: "Skill" })),
        ...results.occupations.map((r) => ({ ...r, kind: "Occupation" })),
        ...results.industries.map((r) => ({ ...r, kind: "Industry" })),
      ]
    : [];

  function handleSelect(nodeId: string) {
    focusNode(nodeId);
    setOpen(false);
  }

  return (
    <div ref={containerRef} className="relative w-full max-w-md">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => flatResults.length > 0 && setOpen(true)}
        placeholder="Explore the workforce — try “Generative AI”, “Data Scientist”…"
        className="w-full rounded-xl border border-prism-600/50 bg-prism-900/70 px-4 py-2.5 text-sm text-prism-100
          placeholder:text-prism-400 outline-none transition-colors focus:border-spectrum-violet/70"
      />
      {open && (
        <div className="absolute left-0 right-0 top-full z-30 mt-2 max-h-80 overflow-y-auto rounded-xl border border-prism-600/50 bg-prism-900/95 backdrop-blur-xl shadow-2xl">
          {loading && <div className="px-4 py-3 text-xs text-prism-400">Searching…</div>}
          {!loading && flatResults.length === 0 && (
            <div className="px-4 py-3 text-xs text-prism-400">No matches yet — try another term.</div>
          )}
          {!loading &&
            flatResults.map((r) => (
              <button
                key={r.node_id}
                onClick={() => handleSelect(r.node_id)}
                className="flex w-full items-center justify-between px-4 py-2.5 text-left text-sm text-prism-100 hover:bg-prism-800/70"
              >
                <span>{r.name}</span>
                <span className="text-[10px] uppercase tracking-wide text-prism-400">{r.kind}</span>
              </button>
            ))}
        </div>
      )}
    </div>
  );
}

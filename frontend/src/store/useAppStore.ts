import { create } from "zustand";

/**
 * Global UI state scaffold. Phase 2 adds graph selection/filters state,
 * Phase 3 adds the selected timeline year, Phase 6 adds simulation
 * scenario state — all colocated here rather than prop-drilled.
 */
interface AppState {
  theme: "dark" | "light";
  toggleTheme: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  theme: "dark",
  toggleTheme: () => set({ theme: get().theme === "dark" ? "light" : "dark" }),
}));

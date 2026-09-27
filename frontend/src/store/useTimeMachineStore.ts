import { create } from "zustand";
import { api } from "@/services/api";
import type { SkillSnapshot } from "@/types/graph";

const DEFAULT_YEARS = [2022, 2023, 2024, 2025, 2026];
const PLAY_INTERVAL_MS = 1600;

interface TimeMachineState {
  years: number[];
  currentYear: number;
  playing: boolean;
  loading: boolean;
  snapshotByskillId: Map<number, SkillSnapshot>;
  playTimer: ReturnType<typeof setInterval> | null;

  init: () => Promise<void>;
  setYear: (year: number) => Promise<void>;
  play: () => void;
  pause: () => void;
  toggle: () => void;
}

export const useTimeMachineStore = create<TimeMachineState>((set, get) => ({
  years: DEFAULT_YEARS,
  currentYear: DEFAULT_YEARS[DEFAULT_YEARS.length - 1],
  playing: false,
  loading: false,
  snapshotByskillId: new Map(),
  playTimer: null,

  init: async () => {
    try {
      const yearsRes = await api.getAvailableYears();
      set({ years: yearsRes.years, currentYear: yearsRes.latest });
    } catch {
      // Keep the sensible defaults if the backend isn't reachable yet.
    }
    await get().setYear(get().currentYear);
  },

  setYear: async (year: number) => {
    set({ currentYear: year, loading: true });
    try {
      const snapshot = await api.getWorkforceSnapshot(year);
      const map = new Map(snapshot.skills.map((s) => [s.skill_id, s]));
      set({ snapshotByskillId: map, loading: false });
    } catch {
      set({ loading: false });
    }
  },

  play: () => {
    if (get().playing) return;
    const timer = setInterval(() => {
      const { years, currentYear, setYear, pause } = get();
      const idx = years.indexOf(currentYear);
      const next = years[(idx + 1) % years.length];
      setYear(next);
      if (idx + 1 >= years.length) {
        // Finished one full pass — stop rather than loop forever.
        setTimeout(pause, PLAY_INTERVAL_MS);
      }
    }, PLAY_INTERVAL_MS);
    set({ playing: true, playTimer: timer });
  },

  pause: () => {
    const { playTimer } = get();
    if (playTimer) clearInterval(playTimer);
    set({ playing: false, playTimer: null });
  },

  toggle: () => {
    get().playing ? get().pause() : get().play();
  },
}));

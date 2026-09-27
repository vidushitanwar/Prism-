import { create } from "zustand";

interface DemoModeState {
  running: boolean;
  caption: string;
  stepIndex: number;
  totalSteps: number;
  start: () => void;
  stop: () => void;
  setProgress: (stepIndex: number, totalSteps: number, caption: string) => void;
}

export const useDemoModeStore = create<DemoModeState>((set) => ({
  running: false,
  caption: "",
  stepIndex: 0,
  totalSteps: 0,
  start: () => set({ running: true, stepIndex: 0, caption: "Starting the PRISM demo…" }),
  stop: () => set({ running: false, caption: "" }),
  setProgress: (stepIndex, totalSteps, caption) => set({ stepIndex, totalSteps, caption }),
}));

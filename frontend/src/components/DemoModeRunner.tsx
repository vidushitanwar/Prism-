import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useDemoModeStore } from "@/store/useDemoModeStore";
import { useGraphStore } from "@/store/useGraphStore";
import { useTimeMachineStore } from "@/store/useTimeMachineStore";
import { api } from "@/services/api";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Drives the "🚀 Demo Mode" walkthrough described in the build spec:
 * Search -> Graph -> Node -> Timeline -> Emerging Capability ->
 * Industry Bridge -> Career Wormhole -> Simulation. Every step calls the
 * real API/stores that power the app — this is a guided tour of live
 * data, not a scripted animation over fake screens. It checks `running`
 * between steps so Stop Demo aborts promptly.
 */
export function DemoModeRunner() {
  const navigate = useNavigate();
  const runningRef = useRef(false);

  useEffect(() => {
    const unsubscribe = useDemoModeStore.subscribe((state, prev) => {
      if (state.running && !prev.running) {
        runningRef.current = true;
        runSequence();
      }
      if (!state.running) {
        runningRef.current = false;
      }
    });
    return unsubscribe;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function runSequence() {
    const { setProgress, stop } = useDemoModeStore.getState();
    const totalSteps = 8;
    const step = (n: number, caption: string) => {
      if (!runningRef.current) return false;
      setProgress(n, totalSteps, caption);
      return true;
    };

    try {
      if (!step(1, "Searching the workforce graph for “Generative AI”…")) return;
      navigate("/explore");
      await sleep(900);
      const genAiResults = await api.search("Generative AI");
      const genAiNode = genAiResults.results.skills[0];
      if (genAiNode) await useGraphStore.getState().focusNode(genAiNode.node_id);
      await sleep(1800);

      if (!step(2, "Opening the Retrieval-Augmented Generation node and its related skills…")) return;
      const ragResults = await api.search("Retrieval-Augmented Generation");
      const ragNode = ragResults.results.skills[0];
      if (ragNode) await useGraphStore.getState().focusNode(ragNode.node_id);
      await sleep(2200);

      if (!step(3, "Running the Workforce Time Machine, 2022 → 2026…")) return;
      const tm = useTimeMachineStore.getState();
      await tm.setYear(tm.years[0] ?? 2022);
      tm.play();
      await sleep(9000);
      tm.pause();

      if (!step(4, "Opening the Skill Emergence Detector…")) return;
      navigate("/emerging");
      await sleep(2600);

      if (!step(5, "Locating a Bridge Skill that connects multiple industries…")) return;
      const bridges = await api.getBridgeSkills(1);
      navigate("/explore");
      await sleep(600);
      if (bridges[0]) await useGraphStore.getState().focusNode(`skill:${bridges[0].subject_id}`);
      await sleep(2200);

      if (!step(6, "Opening Career Wormholes — non-obvious occupation transitions…")) return;
      navigate("/routes");
      await sleep(2600);

      if (!step(7, "Heading to the Workforce Shock Simulator — try a Stress Test preset…")) return;
      navigate("/simulate");
      await sleep(2600);

      if (!step(8, "Demo complete. Explore freely, or run a Stress Test above.")) return;
      await sleep(2600);
    } finally {
      stop();
    }
  }

  return null;
}

import { Routes, Route } from "react-router-dom";
import Landing from "@/pages/Landing";
import Explore from "@/pages/Explore";
import EmergingSkills from "@/pages/EmergingSkills";
import GhostSkills from "@/pages/GhostSkills";
import StructuralShifts from "@/pages/StructuralShifts";
import CareerRoutes from "@/pages/CareerRoutes";
import WorkforceRadar from "@/pages/WorkforceRadar";
import Insights from "@/pages/Insights";
import TalentDna from "@/pages/TalentDna";
import Simulator from "@/pages/Simulator";
import ComingSoon from "@/pages/ComingSoon";
import { CommandPalette } from "@/components/CommandPalette";
import { DemoModeRunner } from "@/components/DemoModeRunner";
import { DemoModeOverlay } from "@/components/DemoModeOverlay";

export default function App() {
  return (
    <>
      <CommandPalette />
      <DemoModeRunner />
      <DemoModeOverlay />
      <Routes>
        <Route path="/" element={<Landing />} />

        {/* Built in Phase 2: interactive Workforce Map + search */}
        <Route path="/explore" element={<Explore />} />

        {/* Built in Phase 3: Skill Emergence Detector */}
        <Route path="/emerging" element={<EmergingSkills />} />

        {/* Built in Phase 3: Ghost Skills */}
        <Route path="/ghost-skills" element={<GhostSkills />} />

        {/* Built in Phase 4: Workforce Radar intelligence dashboard */}
        <Route path="/radar" element={<WorkforceRadar />} />

        {/* Built in Phase 4: Structural Shift Detector + Why Did This Change? */}
        <Route path="/structural-shifts" element={<StructuralShifts />} />

        {/* Built in Phase 4: Career Route Planner & Career Wormholes */}
        <Route path="/routes" element={<CareerRoutes />} />

        {/* Built in Phase 6: Workforce Shock Simulator */}
        <Route path="/simulate" element={<Simulator />} />

        {/* Built in Phase 5: Geography / Education intelligence */}
        <Route path="/insights" element={<Insights />} />

        {/* Built in Phase 5: Talent DNA */}
        <Route path="/talent-dna" element={<TalentDna />} />

        <Route
          path="*"
          element={<ComingSoon title="Page not found" phase="404" />}
        />
      </Routes>
    </>
  );
}

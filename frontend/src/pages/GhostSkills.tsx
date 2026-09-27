import { AppNav } from "@/components/AppNav";
import { SkillSignalList } from "@/components/SkillSignalList";
import { api } from "@/services/api";

export default function GhostSkills() {
  return (
    <div className="min-h-screen">
      <AppNav />
      <SkillSignalList
        title="Ghost Skills"
        subtitle="Legacy & Declining Capabilities"
        accentColor="rose"
        fetcher={(year) => api.getDecliningSkills(15, year)}
        emptyLabel="No declining/ghost skills detected for this year in the seeded dataset."
      />
    </div>
  );
}

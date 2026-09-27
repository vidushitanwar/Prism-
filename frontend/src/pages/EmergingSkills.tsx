import { AppNav } from "@/components/AppNav";
import { SkillSignalList } from "@/components/SkillSignalList";
import { api } from "@/services/api";

export default function EmergingSkills() {
  return (
    <div className="min-h-screen">
      <AppNav />
      <SkillSignalList
        title="Emerging Skills"
        subtitle="Skill Emergence Detector"
        accentColor="violet"
        fetcher={(year) => api.getEmergingSkills(15, year)}
        emptyLabel="No emerging skills detected for this year in the seeded dataset."
      />
    </div>
  );
}

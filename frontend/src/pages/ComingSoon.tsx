import { useNavigate } from "react-router-dom";
import { AppNav } from "@/components/AppNav";

export default function ComingSoon({ title, phase }: { title: string; phase: string }) {
  const navigate = useNavigate();
  return (
    <div className="flex h-screen flex-col">
      <AppNav />
      <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
        <p className="mb-3 text-xs uppercase tracking-[0.3em] text-spectrum-amber">{phase}</p>
        <h1 className="font-display text-3xl text-prism-100">{title}</h1>
        <p className="mt-3 max-w-md text-sm text-prism-400">
          This module is scheduled for a later build phase and is not implemented yet in this
          checkpoint. It is intentionally labeled rather than faked.
        </p>
        <button className="btn-secondary mt-8" onClick={() => navigate("/")}>
          ← Back to Landing
        </button>
      </div>
    </div>
  );
}

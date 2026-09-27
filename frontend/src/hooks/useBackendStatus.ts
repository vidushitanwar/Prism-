import { useEffect, useState } from "react";
import { api } from "@/services/api";

export type BackendStatus = "checking" | "online" | "offline";

/**
 * Pings the FastAPI backend on mount so the UI can honestly reflect
 * whether the API + DB are reachable, instead of a decorative indicator.
 */
export function useBackendStatus() {
  const [status, setStatus] = useState<BackendStatus>("checking");
  const [dbStatus, setDbStatus] = useState<BackendStatus>("checking");

  useEffect(() => {
    let cancelled = false;

    api
      .health()
      .then(() => !cancelled && setStatus("online"))
      .catch(() => !cancelled && setStatus("offline"));

    api
      .healthDb()
      .then((res) => !cancelled && setDbStatus(res.database === "connected" ? "online" : "offline"))
      .catch(() => !cancelled && setDbStatus("offline"));

    return () => {
      cancelled = true;
    };
  }, []);

  return { status, dbStatus };
}

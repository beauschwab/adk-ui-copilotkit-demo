"use client";

import { useEffect, useRef, useState } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { useSession } from "@/lib/auth-client";

interface CopilotKitProviderProps {
  children: React.ReactNode;
}

/**
 * CopilotKit provider that injects the x-user-id header and backend preference.
 *
 * Uses client-side useSession() hook to reactively get the user ID,
 * ensuring the header is set correctly after login without requiring
 * a full page reload.
 *
 * This header is forwarded by CopilotKit to the backend (ADK or LangGraph),
 * where user_id_extractor reads it to create per-user sessions.
 */
export function CopilotKitProvider({ children }: CopilotKitProviderProps) {
  const { data: session, isPending } = useSession();
  const userId = session?.user?.email;
  const prevUserIdRef = useRef<string | undefined>(undefined);
  const mountTimeRef = useRef<number>(Date.now());

  // Get backend preference from localStorage
  const [backend, setBackend] = useState<"adk" | "langgraph">("adk");

  useEffect(() => {
    // Load backend preference
    const saved = localStorage.getItem("agent-backend");
    if (saved === "langgraph") {
      setBackend("langgraph");
    }

    // Listen for storage changes (when settings are saved)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "agent-backend" && (e.newValue === "adk" || e.newValue === "langgraph")) {
        setBackend(e.newValue);
        console.log("[CopilotKit:backend] switched to:", e.newValue);
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  // Log auth state transitions for debugging
  useEffect(() => {
    const elapsed = Date.now() - mountTimeRef.current;

    if (isPending) {
      console.log("[CopilotKit:auth] session loading...", { elapsed: `${elapsed}ms` });
      return;
    }

    const prevUserId = prevUserIdRef.current;
    const transition =
      !prevUserId && userId
        ? "signed-in"
        : prevUserId && !userId
          ? "signed-out"
          : prevUserId !== userId
            ? "user-changed"
            : "no-change";

    if (transition !== "no-change") {
      console.log("[CopilotKit:auth] state transition:", {
        transition,
        userId: userId ?? "(none)",
        prevUserId: prevUserId ?? "(none)",
        elapsed: `${elapsed}ms`,
        headersWillUpdate: !!userId,
        backend,
      });
    }

    prevUserIdRef.current = userId;
  }, [userId, isPending, backend]);

  // Warn if headers might not propagate (CopilotKit gotcha)
  useEffect(() => {
    if (userId && prevUserIdRef.current === undefined) {
      console.log("[CopilotKit:auth] headers now configured:", {
        "x-user-id": userId,
        "x-agent-backend": backend,
        note: "If requests still fail, ensure CopilotKit re-initialises on header changes",
      });
    }
  }, [userId, backend]);

  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="knowsee_agent"
      publicLicenseKey={process.env.NEXT_PUBLIC_COPILOTKIT_PUBLIC_KEY}
      headers={
        userId
          ? {
              "x-user-id": userId,
              "x-agent-backend": backend,
            }
          : undefined
      }
    >
      {children}
    </CopilotKit>
  );
}

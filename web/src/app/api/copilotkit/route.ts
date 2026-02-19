import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

// Use empty adapter since we're routing to a single agent
const serviceAdapter = new ExperimentalEmptyAdapter();

// Backend agent URLs - support both ADK and LangGraph
const adkUrl = process.env.AGENT_URL || "http://localhost:8000";
const langgraphUrl =
  process.env.LANGGRAPH_AGENT_URL || process.env.AGENT_URL_LANGGRAPH || "http://localhost:8001";

if (!adkUrl) {
  throw new Error(
    "AGENT_URL environment variable is required. Set it in web/.env.development or your deployment environment.",
  );
}

// Track request count for correlation
let requestCount = 0;

// Next.js App Router API endpoint
export const POST = async (req: NextRequest) => {
  const requestId = ++requestCount;
  const userId = req.headers.get("x-user-id");

  // Get backend preference from request header (set by client)
  const preferredBackend = req.headers.get("x-agent-backend") || "adk";

  // Log incoming request with auth context
  console.log(`[CopilotKit:route] request #${requestId}:`, {
    auth: userId ? "authenticated" : "anonymous",
    userId: userId ?? "(none)",
    backend: preferredBackend,
  });

  // Warn if request is unauthenticated
  if (!userId) {
    console.warn(`[CopilotKit:route] request #${requestId}: missing x-user-id header`, {
      hint: "Check CopilotKitProvider auth state - user may not be logged in or session not loaded",
    });
  }

  // Select agent URL based on preference
  const agentUrl = preferredBackend === "langgraph" ? langgraphUrl : adkUrl;

  console.log(`[CopilotKit:route] routing to ${preferredBackend} backend: ${agentUrl}`);

  // Create runtime with selected backend
  const runtime = new CopilotRuntime({
    agents: {
      knowsee_agent: new HttpAgent({ url: agentUrl }),
    },
  });

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};

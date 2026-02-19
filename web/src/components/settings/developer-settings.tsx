"use client";

import { useState, useEffect } from "react";
import { Code2Icon, ServerIcon, CheckIcon } from "lucide-react";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type Backend = "adk" | "langgraph";

export function DeveloperSettings() {
  const [selectedBackend, setSelectedBackend] = useState<Backend>("adk");
  const [savedBackend, setSavedBackend] = useState<Backend>("adk");
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved">("idle");

  // Load saved preference on mount
  useEffect(() => {
    const saved = localStorage.getItem("agent-backend") as Backend | null;
    if (saved === "adk" || saved === "langgraph") {
      setSelectedBackend(saved);
      setSavedBackend(saved);
    }
  }, []);

  const hasChanges = selectedBackend !== savedBackend;

  const handleSave = () => {
    setSaveStatus("saving");

    // Save to localStorage
    localStorage.setItem("agent-backend", selectedBackend);
    setSavedBackend(selectedBackend);

    // Show saved state briefly
    setTimeout(() => {
      setSaveStatus("saved");
      setTimeout(() => {
        setSaveStatus("idle");
      }, 2000);
    }, 300);
  };

  const handleReset = () => {
    setSelectedBackend(savedBackend);
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-sidebar-border px-8 py-6">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-lg bg-accent">
            <Code2Icon className="size-5 text-foreground" />
          </div>
          <div>
            <h2 className="text-lg font-semibold tracking-tight">Developer</h2>
            <p className="text-sm text-muted-foreground">
              Advanced settings for developers
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 space-y-8 overflow-y-auto px-8 py-6">
        {/* Backend Selection */}
        <div className="space-y-4">
          <div>
            <h3 className="text-base font-medium">Agent Backend</h3>
            <p className="text-sm text-muted-foreground">
              Choose which AI agent framework powers the chat
            </p>
          </div>

          <RadioGroup
            value={selectedBackend}
            onValueChange={(value) => setSelectedBackend(value as Backend)}
            className="space-y-3"
          >
            {/* ADK Option */}
            <div
              className={cn(
                "relative flex cursor-pointer items-start space-x-3 rounded-lg border-2 p-4 transition-all",
                selectedBackend === "adk"
                  ? "border-primary bg-accent/50"
                  : "border-sidebar-border hover:border-accent",
              )}
              onClick={() => setSelectedBackend("adk")}
            >
              <RadioGroupItem value="adk" id="backend-adk" className="mt-0.5" />
              <Label
                htmlFor="backend-adk"
                className="flex flex-1 cursor-pointer flex-col space-y-1"
              >
                <div className="flex items-center gap-2">
                  <ServerIcon className="size-4" />
                  <span className="font-medium">Google ADK (Default)</span>
                  {savedBackend === "adk" && (
                    <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                      Active
                    </span>
                  )}
                </div>
                <span className="text-sm text-muted-foreground">
                  Production-ready implementation using Google's Agent Development Kit.
                  Includes extended thinking, tool delegation, and AG-UI protocol support.
                </span>
                <div className="pt-2 text-xs text-muted-foreground">
                  <div className="font-medium">Features:</div>
                  <ul className="ml-4 mt-1 list-disc space-y-0.5">
                    <li>AgentTool pattern for clean sub-agent delegation</li>
                    <li>Built-in callbacks for context injection</li>
                    <li>Native Google Search grounding</li>
                    <li>Optimized for Gemini models</li>
                  </ul>
                </div>
              </Label>
            </div>

            {/* LangGraph Option */}
            <div
              className={cn(
                "relative flex cursor-pointer items-start space-x-3 rounded-lg border-2 p-4 transition-all",
                selectedBackend === "langgraph"
                  ? "border-primary bg-accent/50"
                  : "border-sidebar-border hover:border-accent",
              )}
              onClick={() => setSelectedBackend("langgraph")}
            >
              <RadioGroupItem
                value="langgraph"
                id="backend-langgraph"
                className="mt-0.5"
              />
              <Label
                htmlFor="backend-langgraph"
                className="flex flex-1 cursor-pointer flex-col space-y-1"
              >
                <div className="flex items-center gap-2">
                  <Code2Icon className="size-4" />
                  <span className="font-medium">LangGraph</span>
                  {savedBackend === "langgraph" && (
                    <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                      Active
                    </span>
                  )}
                  <span className="rounded-full bg-yellow-500/10 px-2 py-0.5 text-xs font-medium text-yellow-600 dark:text-yellow-500">
                    Experimental
                  </span>
                </div>
                <span className="text-sm text-muted-foreground">
                  Alternative implementation using LangChain's LangGraph framework.
                  Provides explicit graph structure and state management.
                </span>
                <div className="pt-2 text-xs text-muted-foreground">
                  <div className="font-medium">Features:</div>
                  <ul className="ml-4 mt-1 list-disc space-y-0.5">
                    <li>Explicit state graph with conditional routing</li>
                    <li>PostgreSQL checkpointer for persistence</li>
                    <li>Flexible reducer system for state management</li>
                    <li>Compatible with LangChain ecosystem</li>
                  </ul>
                </div>
              </Label>
            </div>
          </RadioGroup>

          {/* Info Box */}
          <div className="rounded-lg border border-sidebar-border bg-accent/30 p-4">
            <div className="flex gap-3">
              <div className="mt-0.5 text-muted-foreground">
                <svg
                  className="size-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="flex-1 space-y-1 text-sm">
                <p className="font-medium">Backend Switching</p>
                <p className="text-muted-foreground">
                  Changing the backend will affect new chat sessions. Existing sessions
                  will continue using their original backend. A page refresh is required
                  after saving changes.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer - Save/Cancel buttons */}
      {hasChanges && (
        <div className="flex items-center justify-between border-t border-sidebar-border bg-accent/20 px-8 py-4">
          <p className="text-sm text-muted-foreground">
            You have unsaved changes
          </p>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              disabled={saveStatus === "saving"}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleSave}
              disabled={saveStatus === "saving"}
            >
              {saveStatus === "saving" ? (
                <>
                  <div className="mr-2 size-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Saving...
                </>
              ) : saveStatus === "saved" ? (
                <>
                  <CheckIcon className="mr-2 size-4" />
                  Saved
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

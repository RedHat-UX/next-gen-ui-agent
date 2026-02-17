import { useState, useEffect } from "react";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { useToolResultParser } from "./hooks";
import { ErrorDisplay, LoadingDisplay, ComponentRenderer } from "./components";

interface AppProps {
  appName: string;
}

export function App({ appName }: AppProps) {
  const [toolResult, setToolResult] = useState<CallToolResult | null>(null);

  // useApp automatically enables auto-resize by default
  const { error: appError } = useApp({
    appInfo: { name: appName, version: "1.0.0" },
    capabilities: {},
    onAppCreated: (app) => {
      app.ontoolresult = async (result) => {
        setToolResult(result);
      };
      app.onerror = console.error;
    },
  });

  const { componentConfigs, error, isLoading } = useToolResultParser(toolResult);

  // Force reflow after content renders to trigger ResizeObserver
  useEffect(() => {
    if (componentConfigs.length > 0) {
      // Wait for DOM to update completely before triggering resize detection
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          // Force a reflow to ensure browser has measured the new content
          document.body.offsetHeight;
        });
      });
    }
  }, [componentConfigs]);

  if (appError) {
    return <ErrorDisplay error={appError.message} />;
  }

  if (error) {
    return <ErrorDisplay error={error} />;
  }

  if (isLoading || componentConfigs.length === 0) {
    return <LoadingDisplay message={`Loading ${componentConfigs.length === 1 ? 'component' : 'components'}...`} />;
  }

  // Auto-enable spacing for multiple components
  return <ComponentRenderer configs={componentConfigs} spacing={componentConfigs.length > 1} />;
}

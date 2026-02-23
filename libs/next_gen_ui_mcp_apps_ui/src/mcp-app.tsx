import { useState, useEffect } from "react";
import ReactDOM from "react-dom/client";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { useToolResultParser } from "./utils/useToolResultParser";
import { ErrorDisplay, LoadingDisplay, ComponentRenderer } from "./utils/component-renderer";

function App({ appName }: { appName: string }) {
  const [toolResult, setToolResult] = useState<CallToolResult | null>(null);

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

  useEffect(() => {
    if (componentConfigs.length > 0) {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
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
    return <LoadingDisplay message={`Loading ${componentConfigs.length === 1 ? "component" : "components"}...`} />;
  }

  return <ComponentRenderer configs={componentConfigs} spacing={componentConfigs.length > 1} />;
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App appName="Next Gen UI" />);

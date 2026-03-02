import { useState, useEffect } from "react";
import ReactDOM from "react-dom/client";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { useToolResultParser } from "./utils/useToolResultParser";
import { ErrorDisplay, LoadingDisplay, ComponentRenderer } from "./component-renderer";
import { AppContextProvider } from "./AppContext";
import "./global.css";
import "./mcp-app.css";

function App({ appName }: { appName: string }) {
  const [toolResult, setToolResult] = useState<CallToolResult | null>(null);
  const [toolResultKey, setToolResultKey] = useState(0);

  const { app, isConnected, error: appError } = useApp({
    appInfo: { name: appName, version: "1.0.0" },
    capabilities: {},
    onAppCreated: (appInstance) => {
      appInstance.ontoolresult = async (result) => {
        setToolResult(result as CallToolResult);
        setToolResultKey((k) => k + 1);
      };
      appInstance.onerror = console.error;
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

  if (!isConnected) {
    return <LoadingDisplay message="Connecting to host..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} />;
  }

  if (isLoading || componentConfigs.length === 0) {
    return <LoadingDisplay message="Loading components..." />;
  }

  return (
    <AppContextProvider app={app}>
      <ComponentRenderer
        key={toolResultKey}
        configs={componentConfigs}
        spacing={componentConfigs.length > 1}
      />
    </AppContextProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App appName="Next Gen UI" />);

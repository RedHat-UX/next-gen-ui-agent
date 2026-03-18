import { createContext, useContext, useState, useEffect } from "react";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { useToolResultParser } from "./utils/useToolResultParser";
import { ErrorDisplay, LoadingDisplay, ComponentRenderer } from "./component-renderer";
import { ComponentHandlerRegistryProvider } from '@rhngui/patternfly-react-renderer';

const McpAppContext = createContext<App | null>(null);

export function useMcpApp(): App | null {
  return useContext(McpAppContext);
}

interface McpAppProviderProps {
  appName: string;
}

export function McpAppProvider({ appName }: McpAppProviderProps) {
  const [app, setApp] = useState<App | null>(null);
  const [toolResult, setToolResult] = useState<CallToolResult | null>(null);
  const [toolResultKey, setToolResultKey] = useState(0);

  const { isConnected, error: appError } = useApp({
    appInfo: { name: appName, version: "1.0.0" },
    capabilities: {},
    onAppCreated: (appInstance) => {
      setApp(appInstance);
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

  /**
   * Callback to update the tool result from user action handlers in the ComponentRenderer.
   * 
   * @param result 
   */
  const handleToolResultUpdate = (result: CallToolResult) => {
    setToolResult(result);
    setToolResultKey((k) => k + 1);
  };

  return (
    <McpAppContext.Provider value={app}>
      <ComponentHandlerRegistryProvider>
        <ComponentRenderer
          app={app}
          key={toolResultKey}
          configs={componentConfigs}
          spacing={componentConfigs.length > 1}
          onToolResultUpdate={handleToolResultUpdate}
        />
      </ComponentHandlerRegistryProvider>
    </McpAppContext.Provider>
  );
}

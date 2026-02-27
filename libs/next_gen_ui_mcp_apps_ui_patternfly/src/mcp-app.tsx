import ReactDOM from "react-dom/client";
import { McpAppProvider } from "./AppContext";
import "./global.css";
import "./mcp-app.css";

import { useApp } from "@modelcontextprotocol/ext-apps/react";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { useToolResultParser } from "./utils/useToolResultParser";
import { ErrorDisplay, LoadingDisplay, ComponentRenderer } from "./utils/component-renderer";
import { ComponentHandlerRegistryProvider }from '@rhngui/patternfly-react-renderer';


function App({ appName }: { appName: string }) {
  const [toolResult, setToolResult] = useState<CallToolResult | null>(null);

  const { app: app, error: appError } = useApp({
    appInfo: { name: appName, version: "1.0.0" },
    capabilities: {},
    onAppCreated: (app) => {
      app.ontoolresult = async (result) => {
        setToolResult(result);
        // TODO I thing ComponentRenderer must be created here, or updated from here, to be able to rerender the component after each tool result is received. Also `app` has to be passed to it from here, as it is really initialized.
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

  console.log("Initializing MCP App app ...", app);
  // TODO `app` is null here during the first NGUI component rendering, it is not null for subsequent ones. It must be provided to the ComponentRenderer from onAppCreated callback or even app.ontoolresult callback.
  // I think <LoadingDisplay> should be always returned here, and ComponentRenderer initiated from `app.ontoolresult` callback once there are some data for rendering. 
  // Or at least <ComponentRenderer> can be created here (without app passed here), and updated from `app.ontoolresult` callback.
  return <ComponentHandlerRegistryProvider><ComponentRenderer app={app} configs={componentConfigs} spacing={componentConfigs.length > 1} /></ComponentHandlerRegistryProvider>;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <McpAppProvider appName="Next Gen UI MCP App (React + PatternFly)" />
);

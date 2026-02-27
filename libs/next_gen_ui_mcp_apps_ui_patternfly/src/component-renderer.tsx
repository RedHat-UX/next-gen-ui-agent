import DynamicComponent from "@rhngui/patternfly-react-renderer";
import {useComponentHandlerRegistry} from '@rhngui/patternfly-react-renderer';
import type { App } from "@modelcontextprotocol/ext-apps/react";

interface ErrorDisplayProps {
  error: string;
}

export function ErrorDisplay({ error }: ErrorDisplayProps) {
  return (
    <div className="ngui-error">
      <h1>Error</h1>
      <p>{error}</p>
    </div>
  );
}

interface LoadingDisplayProps {
  message?: string;
}

export function LoadingDisplay({ message = "Loading..." }: LoadingDisplayProps) {
  return (
    <div className="ngui-loading">
      <p>{message}</p>
    </div>
  );
}

interface ComponentRendererProps {
  app: App | null;
  configs: any[];
  spacing?: boolean;
}

export function ComponentRenderer({ app, configs, spacing = false }: ComponentRendererProps) {

  console.log("Initializing component renderer ...");
  // TODO allow to add handlers more easily by consuments of this MCP Apps renderer, ideally through dedicated info in passed in NGUI `config`
  const registry = useComponentHandlerRegistry();
  registry.registerItemClick("cve-list", (event, payload) => {
    console.log("Item click handler – full payload:", payload);
    if (payload.fields["cve"]?.value) {
      app?.callServerTool({
        name: "cve-detail",
        arguments: {
          cve_id: payload.fields["cve"]?.value,
        },
      });
    }
  });

  return (
    <div className="ngui-render-root">
      {configs.map((config, index) => (
        
        <div
          key={config.id || index}
          className={spacing ? "ngui-block ngui-block--spaced" : "ngui-block"}
        >
          <DynamicComponent config={config} />
        </div>
      ))}
    </div>
  );
}

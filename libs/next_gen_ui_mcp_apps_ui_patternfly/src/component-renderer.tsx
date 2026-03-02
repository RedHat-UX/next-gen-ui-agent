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
  // # TODO PoC code: allows to add action handlers by consuments of this MCP Apps renderer, through dedicated section in the NGUI `config` UI component json
  const registry = useComponentHandlerRegistry();
  for (const config of configs) {
    // TODO add all the config structure validations ...
    if (config.actions?.item_click) {
      console.log("Registering item click handler for component type:", config.input_data_type);
      const action = config.actions.item_click;
      if (action.type === "tool_call") {
        registry.registerItemClick(config.input_data_type, (event, payload) => {
          console.log("Item click handler for component type ", config.input_data_type, " – full payload:", payload);
          
          const args: Record<string, any> = {};
          if (action.arguments) {
            for(const argumentKey of Object.keys(action.arguments)) {
              args[argumentKey] = payload.fields[action.arguments[argumentKey]]?.value;
            }
          }
          console.log("Calling tool:", action.tool, " with arguments:", args);
          app?.callServerTool({
            name: action.tool,
            arguments: args,
          });  
        });
      } else {
        // TODO support other item click types like "message" to generate LLM message, "update-model-context" to update LLM context, or "open-link" to open an URL
        console.error("Item click handler for component type:", config.input_data_type, " – unsupported action type:", action.type);
      }
    } else {
      // TODO support other UI component user action types like "componet_actions", "item_actions", "item_field_clicks", "item_field_actions", see https://docs.google.com/document/d/1-3ZZfd-K2kK4CjerVn6SpqUa3CGWh6WBKrvOPM_EzOU
      console.error("User action handler for component type:", config.input_data_type, " – unsupported user action");
    }
  }
  
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

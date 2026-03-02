import DynamicComponent from "@rhngui/patternfly-react-renderer";

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
  configs: any[];
  spacing?: boolean;
}

export function ComponentRenderer({ configs, spacing = false }: ComponentRendererProps) {
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

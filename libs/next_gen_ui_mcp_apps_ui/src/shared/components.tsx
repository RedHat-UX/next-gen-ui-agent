import DynamicComponent from "@rhngui/patternfly-react-renderer";

interface ErrorDisplayProps {
  error: string;
}

export function ErrorDisplay({ error }: ErrorDisplayProps) {
  return (
    <div style={{ padding: "20px", color: "red" }}>
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
    <div style={{ padding: "20px" }}>
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
    <div style={{ padding: "20px" }}>
      {configs.map((config, index) => (
        <div
          key={config.id || index}
          style={spacing ? { marginBottom: "20px" } : undefined}
        >
          <DynamicComponent config={config} />
        </div>
      ))}
    </div>
  );
}

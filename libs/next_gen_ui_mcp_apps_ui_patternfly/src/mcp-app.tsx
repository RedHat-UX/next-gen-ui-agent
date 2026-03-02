import ReactDOM from "react-dom/client";
import { McpAppProvider } from "./AppContext";
import "./global.css";
import "./mcp-app.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <McpAppProvider appName="Next Gen UI MCP App (React + PatternFly)" />
);

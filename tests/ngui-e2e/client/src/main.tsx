import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";

import "@patternfly/react-core/dist/styles/base.css";
import "@patternfly/chatbot/dist/css/main.css";

// Register NGUI web components
import "ngui-web-components/elements/index.js";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);

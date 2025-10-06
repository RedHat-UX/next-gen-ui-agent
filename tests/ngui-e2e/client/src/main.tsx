import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";

import "@patternfly/react-core/dist/styles/base.css";
import "@patternfly/chatbot/dist/css/main.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);

/**
 * Next Gen UI MCP App (vanilla JS) using RHDS renderer.
 * Renders component HTML from MCP tool results (server must use --component-system rhds).
 * No PatternFly; uses Red Hat Design System web components only.
 */
import {
  App,
  applyDocumentTheme,
  applyHostFonts,
  applyHostStyleVariables,
  type McpUiHostContext,
} from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { parseToolResult } from "./utils/tool-result-parser.js";
import {
  renderErrorDisplay,
  renderLoadingDisplay,
  renderHtmlContents,
} from "./utils/components.js";
import "./global.css";
import "./mcp-app.css";

const APP_NAME = "Next Gen UI (Vanilla JS)";
const rootEl = document.getElementById("root");
if (!rootEl) {
  throw new Error("Root element #root not found");
}
const root = rootEl as HTMLElement;

const SPINNER_LOAD_TIMEOUT_MS = 8000;

function whenSpinnerDefined(): Promise<void> {
  if (customElements.get("rh-spinner")) return Promise.resolve();
  return Promise.race([
    customElements.whenDefined("rh-spinner").then(() => {}),
    new Promise<void>((_, reject) =>
      setTimeout(
        () => reject(new Error("rh-spinner load timeout; check CSP allows https://cdn.jsdelivr.net")),
        SPINNER_LOAD_TIMEOUT_MS
      )
    ),
  ]);
}

function handleHostContextChanged(ctx: McpUiHostContext) {
  if (ctx.theme) {
    applyDocumentTheme(ctx.theme);
  }
  if (ctx.styles?.variables) {
    applyHostStyleVariables(ctx.styles.variables);
  }
  if (ctx.styles?.css?.fonts) {
    applyHostFonts(ctx.styles.css.fonts);
  }
  if (ctx.safeAreaInsets) {
    root.style.paddingTop = `${ctx.safeAreaInsets.top}px`;
    root.style.paddingRight = `${ctx.safeAreaInsets.right}px`;
    root.style.paddingBottom = `${ctx.safeAreaInsets.bottom}px`;
    root.style.paddingLeft = `${ctx.safeAreaInsets.left}px`;
  }
}

function render(
  toolResult: CallToolResult | null,
  appError: string | null
): void {
  if (appError) {
    root.replaceChildren(renderErrorDisplay(appError));
    return;
  }

  const { htmlContents, error, isLoading } = parseToolResult(toolResult);

  if (error) {
    root.replaceChildren(renderErrorDisplay(error));
    return;
  }

  if (isLoading || htmlContents.length === 0) {
    const message = `Loading ${htmlContents.length === 1 ? "component" : "components"}...`;
    whenSpinnerDefined()
      .then(() => {
        root.replaceChildren(renderLoadingDisplay(message));
      })
      .catch((e) => {
        console.error(e);
        const fallback = document.createElement("div");
        fallback.style.padding = "20px";
        fallback.textContent = message;
        root.replaceChildren(fallback);
      });
    return;
  }

  const spacing = htmlContents.length > 1;
  root.replaceChildren(renderHtmlContents(htmlContents, spacing));

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      void root.offsetHeight;
    });
  });
}

const app = new App({ name: APP_NAME, version: "1.0.0" });

app.onteardown = async () => {
  console.info("App is being torn down");
  return {};
};

app.ontoolresult = (result: CallToolResult) => {
  render(result, null);
};

app.onerror = (err: unknown) => {
  console.error(err);
  render(null, err instanceof Error ? err.message : String(err));
};

app.onhostcontextchanged = handleHostContextChanged;

render(null, null);

app.connect().then(() => {
  const ctx = app.getHostContext();
  if (ctx) {
    handleHostContextChanged(ctx);
  }
});

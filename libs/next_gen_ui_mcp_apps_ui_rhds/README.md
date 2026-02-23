# Next Gen UI MCP App (Vanilla JS) — client for next_gen_ui_rhds_renderer

Vanilla JavaScript MCP App that **displays UI produced by the server-side [next_gen_ui_rhds_renderer](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_rhds_renderer)**. The renderer runs in the Next Gen UI MCP server (`--component-system rhds`) and returns HTML (RHDS web components); this app injects that HTML and loads the RHDS element scripts so `<rh-card>`, `<rh-table>`, etc. render.

> [!TIP]
> For PatternFly React rendering (JSON config → React components), use [next_gen_ui_mcp_apps_ui_patternfly](../next_gen_ui_mcp_apps_ui_patternfly) instead.

## MCP Client Configuration

Add to your MCP client configuration (stdio transport):

```json
{
  "mcpServers": {
    "basic-vanillajs": {
      "command": "npx",
      "args": [
        "-y",
        "--silent",
        "--registry=https://registry.npmjs.org/",
        "@modelcontextprotocol/server-basic-vanillajs",
        "--stdio"
      ]
    }
  }
}
```

### Local Development

To test local modifications, use this configuration (replace `~/code/ext-apps` with your clone path):

```json
{
  "mcpServers": {
    "basic-vanillajs": {
      "command": "bash",
      "args": [
        "-c",
        "cd ~/code/ext-apps/examples/basic-server-vanillajs && npm run build >&2 && node dist/index.js --stdio"
      ]
    }
  }
}
```

## Overview

- Tool registration with a linked UI resource
- Vanilla JS UI using the [`App`](https://modelcontextprotocol.github.io/ext-apps/api/classes/app.App.html) class directly
- App communication APIs: [`callServerTool`](https://modelcontextprotocol.github.io/ext-apps/api/classes/app.App.html#callservertool), [`sendMessage`](https://modelcontextprotocol.github.io/ext-apps/api/classes/app.App.html#sendmessage), [`sendLog`](https://modelcontextprotocol.github.io/ext-apps/api/classes/app.App.html#sendlog), [`openLink`](https://modelcontextprotocol.github.io/ext-apps/api/classes/app.App.html#openlink)
- Theme integration via [`applyDocumentTheme()`](https://modelcontextprotocol.github.io/ext-apps/api/functions/app.applyDocumentTheme.html), [`applyHostStyleVariables()`](https://modelcontextprotocol.github.io/ext-apps/api/functions/app.applyHostStyleVariables.html), and [`applyHostFonts()`](https://modelcontextprotocol.github.io/ext-apps/api/functions/app.applyHostFonts.html)

## Key Files

- [`server.ts`](server.ts) - MCP server with tool and resource registration
- [`rhds-mcp-app.html`](rhds-mcp-app.html) / [`src/mcp-app.ts`](src/mcp-app.ts) - Vanilla JS UI using `App` class

## Getting Started

```bash
npm install
npm run dev
```

## How It Works

1. The server registers a `get-time` tool with metadata linking it to a UI HTML resource (`ui://get-time/mcp-app.html`).
2. When the tool is invoked, the Host renders the UI from the resource.
3. The UI uses the MCP App SDK API to communicate with the host and call server tools.

## Build System

This example bundles into a single HTML file using Vite with `vite-plugin-singlefile` — see [`vite.config.ts`](vite.config.ts). This allows all UI content to be served as a single MCP resource. Alternatively, MCP apps can load external resources by defining [`_meta.ui.csp.resourceDomains`](https://modelcontextprotocol.github.io/ext-apps/api/interfaces/app.McpUiResourceCsp.html#resourcedomains) in the UI resource metadata.

## How RHDS web components are rendered

RHDS (Red Hat Design System) elements like `<rh-card>`, `<rh-table>`, `<rh-spinner>` are **custom elements** (Web Components). In this app they are rendered in three steps:

### 1. Server produces HTML (next_gen_ui_rhds_renderer)

When the MCP server runs with `--component-system rhds`, the Python package **next_gen_ui_rhds_renderer** runs on the server. For each UI block it:

- Takes structured component data (e.g. one-card with title, image, fields).
- Renders it with Jinja2 templates into an **HTML string** that uses RHDS tags, e.g.  
  `<rh-card class="ngui-one-card"><h2 slot="header">…</h2><dl>…</dl></rh-card>`.
- Puts that string in `UIBlock.rendering.content` with `mime_type: "text/html"`.
- Sends the tool result (with `blocks[].rendering`) to the MCP host.

So the client never receives JSON component configs; it receives **ready-made HTML** that references RHDS custom elements.

### 2. App shell pre-loads RHDS element definitions

In **rhds-mcp-app.html** we:

- Define an **import map** so bare specifiers like `@rhds/elements/rh-card/rh-card.js` resolve to the CDN.
- Run a **preload script** (before the app script) that imports the RHDS element modules:
  - `rh-card`, `rh-cta`, `rh-table`, `rh-video-embed`, `rh-audio-player`, `rh-spinner`.

Each of those modules calls `customElements.define("rh-card", …)` (or the corresponding tag). After that, the browser knows how to upgrade `<rh-card>` (and the other tags) when it sees them in the DOM.

### 3. Vanilla app injects the server HTML into the DOM

When the app receives a tool result:

1. **tool-result-parser.ts** reads `toolResult` and pulls out `blocks[].rendering` where `mime_type === "text/html"`. It returns an array of HTML strings (`htmlContents`).
2. **components.ts** `renderHtmlContents(htmlContents, spacing)` creates a wrapper `div`, then for each string does:
   - `child = document.createElement("div")`
   - `child.innerHTML = content`  ← server HTML (with `<rh-card>`, etc.) is inserted here
   - `wrap.appendChild(child)`
3. The wrapper is appended to `#root`.

Because the RHDS custom elements were **already defined** in step 2, the browser automatically **upgrades** any `<rh-card>`, `<rh-table>`, etc. in that HTML: it attaches the custom element’s behavior and shadow DOM (if any), so they render as full RHDS components.

**Important:** Script tags inside the injected HTML (e.g. in the server output) do **not** run when using `innerHTML`. That’s why we pre-load all needed elements in the app shell; we don’t rely on scripts in the server HTML.

### Summary

| Step | Where | What happens |
|------|--------|----------------|
| 1 | MCP server (Python) | next_gen_ui_rhds_renderer turns component data into HTML strings with `<rh-card>`, `<rh-table>`, etc. |
| 2 | rhds-mcp-app.html (browser) | Import map + preload script load RHDS JS from CDN; each module calls `customElements.define(...)`. |
| 3 | mcp-app.ts + components.ts | Parse tool result → get `htmlContents` → set `innerHTML` on a div → browser upgrades the custom elements and they render. |

## Using with next_gen_ui_rhds_renderer

1. **Run the MCP server with RHDS** (so it uses next_gen_ui_rhds_renderer):
   ```bash
   pants run libs/next_gen_ui_mcp/server_example.py --run-args="--component-system rhds --transport streamable-http ..."
   ```

2. **Deploy this app as the MCP UI resource** (from repo root):
   ```bash
   pants run libs/next_gen_ui_mcp:update-ui
   ```
   Or manually (build both PatternFly and RHDS apps, then copy):
   ```bash
   cd libs/next_gen_ui_mcp_apps_ui_rhds && npm run build
   cp dist/rhds-mcp-app.html ../next_gen_ui_mcp/ui_resources/
   ```
   See [next_gen_ui_mcp README](../next_gen_ui_mcp/README.md) for full steps including the PatternFly app.

3. **CSP:** When running the MCP apps host, allow the CDN so RHDS scripts load, e.g.:
   `--csp-resource-domains "https://cdn.jsdelivr.net,https://image.tmdb.org"`  
   If `<rh-card>` etc. do not render, the app will show a timeout error; check that the host CSP allows script from `https://cdn.jsdelivr.net`.

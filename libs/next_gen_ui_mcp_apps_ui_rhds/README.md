# Next Gen UI MCP App (Vanilla JS) — client for next_gen_ui_rhds_renderer

Vanilla JavaScript MCP App that displays UI produced by the [next_gen_ui_rhds_renderer](../next_gen_ui_rhds_renderer), using RHDS web components via the MCP Apps SDK.

## Overview

This module contains the browser-based UI views that render HTML produced by the `next_gen_ui_mcp` Python server when run with `--component-system rhds`. It uses:

- **MCP Apps SDK** - Framework for creating MCP App views
- **Vanilla JS / TypeScript** - No React; uses MCP Apps SDK `App` class directly
- **RHDS Web Components** - `<rh-card>`, `<rh-table>`, `<rh-spinner>`, etc. loaded from CDN
- **Vite** - Build tool with single-file bundling

> [!TIP]
> For PatternFly React rendering (JSON config → React components), use [next_gen_ui_mcp_apps_ui_patternfly](../next_gen_ui_mcp_apps_ui_patternfly) instead.

## Architecture

```
Python MCP Server (--component-system rhds) → UIBlock (HTML content) → MCP Host → HTML View (this module) → innerHTML + RHDS upgrade
```

The views receive tool results containing `UIBlock[]` where each block has:
- `rendering.content` - HTML string with RHDS tags (`<rh-card>`, `<rh-table>`, etc.)
- `rendering.mime_type` - `"text/html"`
- HTML is injected into the DOM; pre-loaded RHDS custom elements auto-upgrade

## Quick Start

### Prerequisites

- Node.js 20+ installed
- Python 3.12+ installed
- Pants build system configured (from project root)

### Quick Commands

**Build UI Resources (All-in-One):**

```bash
# From project root
cd /path/to/next-gen-ui-agent

# Install deps, build, and copy to Python module
pants run libs/next_gen_ui_mcp:update-ui
```

**Or Step-by-Step:**

```bash
# From project root
cd libs/next_gen_ui_mcp_apps_ui_rhds
npm install
npm run build

# Copy to Python module
cp dist/rhds-mcp-app.html ../next_gen_ui_mcp/ui_resources/
```

## Project Structure

```
libs/next_gen_ui_mcp_apps_ui_rhds/
├── package.json              # Dependencies and build scripts
├── tsconfig.json             # TypeScript configuration
├── vite.config.ts            # Vite bundler configuration
├── rhds-mcp-app.html        # HTML entry point (import map, RHDS preload)
├── src/
│   ├── mcp-app.ts           # Entry point: App logic, tool result handling
│   ├── mcp-app.css          # App styles
│   ├── global.css           # Global styles
│   └── utils/
│       ├── tool-result-parser.ts  # Extracts HTML from blocks[].rendering
│       ├── components.ts          # renderHtmlContents()
│       └── types.ts               # Tool result types
└── dist/                     # Build output (gitignored)
    └── rhds-mcp-app.html    # Self-contained HTML file
```

## Source layout

### `rhds-mcp-app.html`
Entry point and app shell. Defines:
- Import map so `@rhds/elements/...` resolves to CDN
- Preload script that imports RHDS element modules (`rh-card`, `rh-cta`, `rh-table`, `rh-video-embed`, `rh-audio-player`, `rh-spinner`) and registers them via `customElements.define()`
- RHDS tokens CSS and rh-table lightdom styles

### `src/mcp-app.ts`
Main app logic. Uses `App` from MCP Apps SDK, parses tool results, calls `renderHtmlContents()`, applies theme.

### `src/utils/tool-result-parser.ts`
**`parseToolResult()`** – reads `app.toolResult`, extracts `blocks[].rendering` where `mime_type === "text/html"`, returns array of HTML strings.

### `src/utils/components.ts`
**`renderHtmlContents(htmlContents, spacing)`** – creates wrapper div, sets `innerHTML` for each HTML string, appends to `#root`.

### `src/utils/types.ts`
TypeScript interfaces for tool result parsing.

## Building

### Prerequisites

```bash
# Install dependencies (one time)
npm install
```

### Build Commands

```bash
# Build the HTML file
npm run build

# Watch mode (auto-rebuild on changes)
npm run watch
```

### Using Pants

```bash
# Build via Pants (from project root)
cd /path/to/next-gen-ui-agent
pants run libs/next_gen_ui_mcp_apps_ui_rhds:build
```

## Development

### Development Mode Workflow

Run these commands in separate terminals for live development:

```bash
# Terminal 1: Watch UI changes (auto-rebuild)
cd libs/next_gen_ui_mcp_apps_ui_rhds
npm run watch

# Terminal 2: Run MCP server with RHDS
cd /path/to/next-gen-ui-agent
pants run libs/next_gen_ui_mcp/server_example.py:extended --run-args="--component-system rhds --transport streamable-http"

# Terminal 3: When UI changes, update resources
pants run libs/next_gen_ui_mcp:update-ui
```

## Build Output

The build process creates a **self-contained HTML file** with:
- Vanilla JS/TS code inlined
- RHDS element scripts loaded from CDN (import map + preload)
- RHDS tokens CSS
- MCP Apps SDK
- No React or PatternFly

This file can be served directly by the MCP server as a resource.

## How RHDS Web Components Are Rendered

RHDS elements like `<rh-card>`, `<rh-table>` are **custom elements** (Web Components). The flow:

1. **Server** – next_gen_ui_rhds_renderer turns component data into HTML with RHDS tags, sets `mime_type: "text/html"`
2. **App shell** – Import map + preload script load RHDS JS from CDN; each module calls `customElements.define(...)`
3. **App logic** – Parse tool result → get HTML strings → `innerHTML` on a div → browser upgrades custom elements

Script tags inside injected HTML do **not** run when using `innerHTML`. That's why all needed elements are pre-loaded in the app shell.

## Data Flow

```
1. MCP Server (--component-system rhds) generates UIBlock with rendering.content = '<rh-card>...</rh-card>', mime_type = 'text/html'
2. Python returns tool result with blocks: [UIBlock, ...]
3. MCP Host reads ui://generate_ui_component/mcp-app.html resource and loads rhds-mcp-app.html in iframe
4. App initializes with MCP Apps SDK
5. Preload script has already registered rh-card, rh-table, etc. via customElements.define
6. parseToolResult() extracts htmlContents from blocks[].rendering
7. renderHtmlContents(htmlContents) sets innerHTML on divs
8. Browser upgrades <rh-card>, <rh-table> etc. → full RHDS components render
```

## Testing the Integration

### 1. Start the MCP Server

```bash
# With streamable-http and RHDS (recommended for MCP Apps)
pants run libs/next_gen_ui_mcp/server_example.py:extended --run-args="--transport streamable-http --component-system rhds --port 8000"

# Ensure CSP allows CDN (default includes https://cdn.jsdelivr.net)
pants run libs/next_gen_ui_mcp/server_example.py:extended --run-args="--transport streamable-http --component-system rhds --csp-resource-domains https://cdn.jsdelivr.net,https://image.tmdb.org"
```

### 2. Connect an MCP Host

**Option A: Claude Desktop**

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "next-gen-ui": {
      "command": "pants",
      "args": ["run", "libs/next_gen_ui_mcp/server_example.py:extended", "--run-args=--component-system rhds --transport stdio"],
      "cwd": "/path/to/next-gen-ui-agent"
    }
  }
}
```

**Option B: Basic Host (for testing)**

Use the [example host](https://github.com/modelcontextprotocol/ext-apps/tree/main/examples/basic-host) from `mcp-ext-apps`:
```bash
cd /path/to/mcp-ext-apps/examples/basic-host
npm install
npm run dev
```

### 3. Test Tool Calls

In your MCP host, execute the `generate_ui_component` tool with:

```json
{
  "user_prompt": "Tell me brief details of Toy Story in a form of a card with image",
  "data": "{\"toy_story\":{\"title\":\"Toy Story\",\"year\":1995,\"plot\":\"A cowboy doll is profoundly threatened...\",\"posterUrl\":\"https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg\"}}",
  "data_type": "movie_detail",
  "data_id": "external_test_id"
}
```

You should see the UI render in an iframe with RHDS components!

## Troubleshooting

### Build fails with "cross-env: command not found"

Run `npm install` to install dependencies.

### Empty output or "Loading..."

Check that:
1. Tool result contains `blocks` array
2. Each block has `rendering.content` as HTML string
3. `rendering.mime_type` is `"text/html"`

### RHDS components not rendering (plain tags visible)

1. **CSP** – Ensure `--csp-resource-domains` includes `https://cdn.jsdelivr.net` so RHDS scripts can load
2. **Preload** – RHDS elements must be registered before injected HTML is parsed; the preload script in rhds-mcp-app.html runs before the app script

### RHDS styles missing

RHDS tokens CSS is loaded from CDN in the HTML. If styles are missing, check CSP allows `https://cdn.jsdelivr.net`.

## Dependencies

### Runtime
- `@modelcontextprotocol/ext-apps` - MCP Apps SDK
- `@modelcontextprotocol/sdk` - MCP SDK types

### Build
- `typescript` - TypeScript compiler
- `vite` - Build tool
- `vite-plugin-singlefile` - Bundles everything into single HTML file
- `cross-env` - Cross-platform environment variables

## Related Documentation

- [MCP Apps Specification](../../specification/2026-01-26/apps.mdx)
- [next_gen_ui_rhds_renderer](../next_gen_ui_rhds_renderer/README.md) - Server-side RHDS renderer
- [Python MCP Server](../next_gen_ui_mcp/README.md)

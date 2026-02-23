---
name: MCP modules refactor
overview: Rename the two MCP UI app libs to patternfly/rhds, standardize HTML output filenames to `<component-system>-mcp-app.html`, make the MCP server serve the correct HTML by component system, and ensure both apps' builds are copied into next_gen_ui_mcp ui_resources for the container image.
todos: []
isProject: false
---

# MCP modules refactor plan

## Scope

- **Rename:** `next_gen_ui_mcp_apps_ui` → `next_gen_ui_mcp_apps_ui_patternfly`, `next_gen_ui_mcp_apps_ui_vanilla` → `next_gen_ui_mcp_apps_ui_rhds`
- **Build outputs:** PatternFly app → `patternfly-mcp-app.html`, RHDS app → `rhds-mcp-app.html`
- **Server:** Use a **single** resource URI; the handler serves the appropriate file based on `component_system`: `json` or `patternfly` → `patternfly-mcp-app.html`, `rhds` → `rhds-mcp-app.html`.
- **Container:** Both UI apps' HTML files must be built and copied into `libs/next_gen_ui_mcp/ui_resources/` when building the MCP module (and thus the container image)

---

## 1. Directory renames and package identities

- **Rename directories** (git mv or equivalent):
  - `libs/next_gen_ui_mcp_apps_ui` → `libs/next_gen_ui_mcp_apps_ui_patternfly`
  - `libs/next_gen_ui_mcp_apps_ui_vanilla` → `libs/next_gen_ui_mcp_apps_ui_rhds`
- **PatternFly app** ([libs/next_gen_ui_mcp_apps_ui_patternfly](libs/next_gen_ui_mcp_apps_ui) after rename):
  - In [package.json](libs/next_gen_ui_mcp_apps_ui/package.json): set `"name": "next_gen_ui_mcp_apps_ui_patternfly"`.
  - In [package-lock.json](libs/next_gen_ui_mcp_apps_ui/package-lock.json): update `name` (or regenerate with `npm install`).
  - Add HTML entry `**patternfly-mcp-app.html**` with same content as current `mcp-app.html` (script stays `/src/mcp-app.tsx`).
  - In `package.json` scripts: use `INPUT=patternfly-mcp-app.html` (e.g. `"build": "cross-env INPUT=patternfly-mcp-app.html vite build"`). Build output will be `dist/patternfly-mcp-app.html`.
  - Update [README.md](libs/next_gen_ui_mcp_apps_ui/README.md): replace all `next_gen_ui_mcp_apps_ui` with `next_gen_ui_mcp_apps_ui_patternfly`, and document output `patternfly-mcp-app.html`.
- **RHDS app** ([libs/next_gen_ui_mcp_apps_ui_rhds](libs/next_gen_ui_mcp_apps_ui_vanilla) after rename):
  - In [package.json](libs/next_gen_ui_mcp_apps_ui_vanilla/package.json): set `"name": "next_gen_ui_mcp_apps_ui_rhds"` (or `next-gen-ui-mcp-apps-ui-rhds` to match current style).
  - In package-lock.json: update `name` (or regenerate).
  - Add HTML entry `**rhds-mcp-app.html**` (same content as current `mcp-app.html`, script `/src/mcp-app.ts`).
  - In `package.json` scripts: use `INPUT=rhds-mcp-app.html`. Build output will be `dist/rhds-mcp-app.html`.
  - Update [README.md](libs/next_gen_ui_mcp_apps_ui_vanilla/README.md): replace references to `next_gen_ui_mcp_apps_ui_vanilla` with `next_gen_ui_mcp_apps_ui_rhds` and to `next_gen_ui_mcp_apps_ui` with `next_gen_ui_mcp_apps_ui_patternfly`; document output `rhds-mcp-app.html` and any copy path to `next_gen_ui_mcp/ui_resources/`.

---

## 2. next_gen_ui_mcp BUILD: build both apps and copy both HTML files

**File:** [libs/next_gen_ui_mcp/BUILD](libs/next_gen_ui_mcp/BUILD)

- `**copy_ui_resources**` `run_shell_command`:
  - `**execution_dependencies`:** add both app build targets:  
  `["libs/next_gen_ui_mcp_apps_ui_patternfly:build", "libs/next_gen_ui_mcp_apps_ui_rhds:build"]`
  - `**command`:** ensure both outputs are copied, e.g.  
  `mkdir -p ui_resources && cp -f ../next_gen_ui_mcp_apps_ui_patternfly/dist/patternfly-mcp-app.html ui_resources/ && cp -f ../next_gen_ui_mcp_apps_ui_rhds/dist/rhds-mcp-app.html ui_resources/ && echo 'UI resources copied successfully'`
- `**update-ui**` `run_shell_command`: run both apps’ build and copy both files:
  - `cd ../next_gen_ui_mcp_apps_ui_patternfly && npm install && npm run build`
  - `cd ../next_gen_ui_mcp_apps_ui_rhds && npm install && npm run build`
  - `cd ../next_gen_ui_mcp && mkdir -p ui_resources`
  - `cp -f ../next_gen_ui_mcp_apps_ui_patternfly/dist/patternfly-mcp-app.html ui_resources/`
  - `cp -f ../next_gen_ui_mcp_apps_ui_rhds/dist/rhds-mcp-app.html ui_resources/`
  - Then `echo` and `ls -lh ui_resources/*.html` as today.
- `**resources()**` `sources`: already `["ui_resources/*.html", "ui_resources/.gitignore"]` — no change; both HTML files will be included.
- **Docker image:** [docker_image](libs/next_gen_ui_mcp/BUILD) depends on `:dist`, which depends on `:lib` → `:copy_ui_resources` and `:ui_resources`. So building the image will run both app builds and copy both HTML files into `ui_resources/`; no Containerfile change needed.

---

## 3. next_gen_ui_mcp server: single resource, file chosen by component system

**File:** [libs/next_gen_ui_mcp/agent.py](libs/next_gen_ui_mcp/agent.py)

- **Mapping:** Treat `json` and `patternfly` the same (JSON is the default and compatible with PatternFly). So:
  - `component_system in ("patternfly", "json")` → serve `patternfly-mcp-app.html`
  - `component_system == "rhds"` → serve `rhds-mcp-app.html`
  - Any other value can fall back to `patternfly-mcp-app.html` or error (e.g. fallback to patternfly for simplicity).
- **Single resource:** Keep **one** resource URI (e.g. `ui://generate_ui_component/mcp-app.html`). Register it once; the handler decides which file to serve based on `self.config.component_system` at request time:
  - Helper: e.g. `_ui_filename_for_component_system(cs)` → `"patternfly-mcp-app.html"` when `cs in ("patternfly", "json")`, else `"rhds-mcp-app.html"` when `cs == "rhds"`, else `"patternfly-mcp-app.html"`.
  - Single `@self.mcp.resource("ui://generate_ui_component/mcp-app.html", ...)` with one handler that reads `UI_RESOURCES_DIR / _ui_filename_for_component_system(self.config.component_system)` and returns its text. So the client always requests the same URI; the server switches which file is served depending on config.
- **Tool meta `resourceUri`:** Always set the same URI (e.g. `"ui://generate_ui_component/mcp-app.html"`) for both tools when a UI is desired. Optionally omit `resourceUri` only when component_system is neither patternfly nor json nor rhds (if you ever want “no UI” for some config). For json/patternfly/rhds, always advertise the single URI so the host loads it; the server then serves the correct HTML.
- **Error message:** If the chosen file is missing, raise `FileNotFoundError` naming the resolved filename (e.g. `patternfly-mcp-app.html` or `rhds-mcp-app.html`) and “Run pants build libs/next_gen_ui_mcp …”.

---

## 4. Documentation and scripts in repo

- **[libs/next_gen_ui_mcp/README.md](libs/next_gen_ui_mcp/README.md):**
  - Replace every `next_gen_ui_mcp_apps_ui` path with `next_gen_ui_mcp_apps_ui_patternfly` (and where relevant mention `next_gen_ui_mcp_apps_ui_rhds`).
  - Update “Manual” steps to build both apps and copy both `patternfly-mcp-app.html` and `rhds-mcp-app.html` into `ui_resources/`.
  - Update “Files generated” to list `patternfly-mcp-app.html` and `rhds-mcp-app.html` instead of `mcp-app.html`.
  - Update troubleshooting “UI resource not found” to reference the appropriate `*-mcp-app.html` and the new paths.
  - Update “Build fails” section to reference both app directories and the new paths.
- **No other scripts or CI** in the repo reference `next_gen_ui_mcp_apps_ui` or `next_gen_ui_mcp_apps_ui_vanilla` by path (only READMEs and BUILD). So after renames and README/BUILD updates, no further script/CI changes are required.

---

## 5. Optional cleanup

- In each app, you can keep or remove the old `mcp-app.html` entry; the build will use the new entry files only. Optionally remove `mcp-app.html` from the app roots to avoid confusion.

---

## Summary of file-level changes


| Area            | Files                                                                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Renames         | `libs/next_gen_ui_mcp_apps_ui` → `libs/next_gen_ui_mcp_apps_ui_patternfly`, `libs/next_gen_ui_mcp_apps_ui_vanilla` → `libs/next_gen_ui_mcp_apps_ui_rhds`      |
| PatternFly app  | New `patternfly-mcp-app.html`, package.json (name + INPUT), package-lock.json, README                                                                         |
| RHDS app        | New `rhds-mcp-app.html`, package.json (name + INPUT), package-lock.json, README                                                                               |
| next_gen_ui_mcp | BUILD (copy_ui_resources + update-ui), agent.py (single resource + handler that picks file by component_system; json/patternfly → patternfly HTML), README.md |


No changes to [Containerfile](libs/next_gen_ui_mcp/Containerfile) or to [main_args_handler.py](libs/next_gen_ui_mcp/main_args_handler.py) for component_system (already supports `--component-system rhds` / patternfly).
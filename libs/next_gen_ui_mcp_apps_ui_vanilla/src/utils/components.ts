/**
 * Vanilla DOM components that display output from next_gen_ui_rhds_renderer.
 *
 * The server (next_gen_ui_rhds_renderer) sends HTML strings; we inject them
 * into the DOM. RHDS web components (rh-card, rh-table, etc.) are pre-loaded
 * in the app shell so they upgrade when the HTML is inserted.
 */

export function renderErrorDisplay(error: string): HTMLElement {
  const div = document.createElement("div");
  div.setAttribute("class", "ngui-error");
  div.style.padding = "var(--rh-space-lg, 24px)";
  div.style.color = "var(--rh-color-text-danger-on-light, #c00)";
  const h1 = document.createElement("h1");
  h1.textContent = "Error";
  const p = document.createElement("p");
  p.textContent = error;
  div.appendChild(h1);
  div.appendChild(p);
  return div;
}

export function renderLoadingDisplay(message = "Loading..."): HTMLElement {
  const wrap = document.createElement("div");
  wrap.setAttribute("class", "ngui-loading");
  wrap.style.padding = "var(--rh-space-lg, 24px)";
  wrap.style.display = "flex";
  wrap.style.flexDirection = "column";
  wrap.style.alignItems = "center";
  wrap.style.gap = "var(--rh-space-md, 16px)";
  wrap.innerHTML = "<rh-spinner></rh-spinner><p class=\"ngui-loading-message\" style=\"margin:0\"></p>";
  const msgEl = wrap.querySelector(".ngui-loading-message");
  if (msgEl) msgEl.textContent = message;
  return wrap;
}

/**
 * Renders HTML produced by next_gen_ui_rhds_renderer (one string per UI block).
 * Script tags in the HTML do not execute when using innerHTML; RHDS elements
 * are pre-loaded in the app shell so <rh-card>, <rh-table>, etc. upgrade.
 */
export function renderHtmlContents(htmlContents: string[], spacing: boolean): HTMLElement {
  const wrap = document.createElement("div");
  wrap.setAttribute("class", "ngui-render-root");
  wrap.style.padding = "var(--rh-space-lg, 24px)";

  for (let i = 0; i < htmlContents.length; i++) {
    const content = htmlContents[i];
    const child = document.createElement("div");
    child.setAttribute("class", "ngui-block");
    if (spacing && i > 0) {
      child.style.marginTop = "var(--rh-space-xl, 24px)";
    }
    child.innerHTML = content;
    wrap.appendChild(child);
  }
  return wrap;
}

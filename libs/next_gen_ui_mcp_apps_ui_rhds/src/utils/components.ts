/**
 * Vanilla DOM components that display output from next_gen_ui_rhds_renderer.
 *
 * The server (next_gen_ui_rhds_renderer) sends HTML strings; we inject them
 * into the DOM. RHDS web components (rh-card, rh-table, etc.) are pre-loaded
 * in the app shell so they upgrade when the HTML is inserted.
 */

import type { TrustedHtml } from "./types.ts";

const template = document.createElement("template");
template.className = "ngui-block-template";

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function trustedHtml(value: string): TrustedHtml {
  return { trusted: true, value };
}

export function html(
  strings: TemplateStringsArray,
  ...values: any[]
): DocumentFragment {
  const result = strings.reduce((acc, str, i) => {
    let value = values[i];

    if (typeof value === "string") {
      value = escapeHtml(value);
    } else if (value?.trusted) {
      value = value.value;
    } else if (value == null) {
      value = "";
    }

    return acc + str + value;
  }, "");

  template.innerHTML = result;
  return template.content.cloneNode(true) as DocumentFragment;
}

export function renderLoadingDisplay(message: string): DocumentFragment {
  return html`
    <div class="ngui-loading">
      <rh-spinner>
        <p>${message}</p>
      </rh-spinner>
    </div>
  `;
}

export function renderErrorDisplay(error: string): DocumentFragment {
  return html`
    <div class="ngui-error">
        ${error}
    </div>
  `;
}

/**
 * Renders HTML from the server (one string per UI block). Uses a single <template>
 * element (created once, reused) and a template literal to build each block's HTML;
 * the template parses the string and we append its .content clone. RHDS elements
 * are pre-loaded so they upgrade.
 */
export function renderHtmlContents(htmlContents: string[]): HTMLElement {
  const wrap = document.createElement("div");
  wrap.setAttribute("class", "ngui-render-root");

  const fragment = htmlContents.reduce(
    (frag, content) => {
      frag.appendChild(
        html`
          <div class="ngui-block">
            ${trustedHtml(content)}
          </div>
        `,
      );
      return frag;
    },
    document.createDocumentFragment(),
  );

  wrap.appendChild(fragment);
  return wrap;
}

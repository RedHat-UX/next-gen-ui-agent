# NGUI Web Components (`@rhngui/web`)

This package contains framework-agnostic web components built with [Lit](https://lit.dev/) that implement the Next Gen UI design system using PatternFly v6 design tokens.

## Overview

The web components wrap or extend [PatternFly Elements](https://github.com/patternfly/patternfly-elements) (v3.0.0 - which are designed to the PatternFly v4 specification) to provide PatternFly v6 styling while leveraging the high performance engineering of the existing component implementations.

This package is consumed by applications (like the e2e test client) as `@rhngui/web` and can be used in any JavaScript/TypeScript project.

## Components

- **`ngui-card`** - Card component for displaying structured content with optional image and header
- **`ngui-image`** - Image component with loading states and accessibility features

## Build System

```bash
npm install
npm run build
```

The build process:
1. Compiles TypeScript to JavaScript
2. Generates Custom Elements Manifest (`custom-elements.json`)
3. Copies built files to `../../tests/ngui-e2e/client/public/ngui-elements/` for consumption by the e2e test client

## Design System

### PatternFly v6 Integration

Components use PatternFly v6 design tokens via CSS custom properties. The approach:

1. **Define PF v6 component properties** in the component's `:host` selector:
   e.g. for card:
   ```css
   :host {
     --pf-v6-c-card--BackgroundColor: var(--pf-t--global--background--color--primary--default);
     --pf-v6-c-card--BorderRadius: var(--pf-t--global--border--radius--medium);
     --pf-v6-c-card--child--PaddingInlineStart: var(--pf-t--global--spacer--lg);
     /* ... etc */
   }
   ```

2. **Apply to wrapped components** using the v6 properties:
   ```css
   pf-card {
     border-radius: var(--pf-v6-c-card--BorderRadius);
     padding-inline-start: var(--pf-v6-c-card--child--PaddingInlineStart);
     /* ... etc */
   }
   ```

This pattern allows wrapping PatternFly Elements (which use v4 styles) while exposing v6 design tokens for theming and customization.

### Styling PatternFly v4 Elements

When wrapping PatternFly Elements components (v4):

- **DO NOT** try to override internal shadow DOM styles
- **DO** define `--pf-v6-c-*` properties that reference `--pf-t--global--*` tokens
- **DO** apply those v6 properties to the wrapped element and custom parts
- **DO** use semantic CSS properties (e.g., `border-radius`, `padding-inline-start`) rather than the element's internal `--pf-c-*` custom properties

Example from `ngui-card.ts:59-135`:
```typescript
static styles = css`
  :host {
    /* Define v6 tokens */
    --pf-v6-c-card--BorderRadius: var(--pf-t--global--border--radius--medium);
  }

  /* Apply to wrapped element */
  pf-card {
    border-radius: var(--pf-v6-c-card--BorderRadius);
  }
`;
```

## Known Issues & Workarounds

### PatternFly Elements Adaptation Challenges

When wrapping PatternFly Elements components, we encountered structural issues that required workarounds:

**Problem**: pf-card's internal `<article>` wrapper prevents proper grid layout control for the horizontal split pattern. The article creates an intermediate container between pf-card and its slotted content, preventing CSS grid from being applied effectively to achieve the PatternFly v6 horizontal split layout.

**Workaround** (`ngui-card.ts:183-191`): Remove the article wrapper by replacing it with its children:
```javascript
async firstUpdated() {
  // WORKAROUND: Remove pf-card's internal article wrapper to enable grid layout.
  // This manipulates pf-card's shadow DOM to make header/body/footer parts
  // direct children of pf-card, allowing proper grid area assignment.
  const pfCard = this.shadowRoot?.querySelector('pf-card');
  await pfCard?.updateComplete;
  const article = pfCard?.shadowRoot?.querySelector('article');
  article?.replaceWith(...article.children);
}
```

This makes pf-card's header/body/footer parts direct children, enabling proper CSS grid area assignment for the horizontal split layout.

**Recommendation for PatternFly Elements**:
- Expose the internal article as a CSS part to allow external styling without DOM manipulation
- Consider making the article wrapper optional or provide a layout mode that supports grid-based layouts
- Add CSS parts for layout containers to enable better customization

## Module Loading

### Vite Incompatibility Workaround

Web components are loaded dynamically via browser's native [import maps](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap) with the `@ngui/web/` prefix. However, **Vite's dev server intercepts dynamic imports**, causing module resolution errors even with `@vite-ignore` comments.

**The Problem:**
```javascript
// ❌ Vite intercepts this even with @vite-ignore
const module = await import(/* @vite-ignore */ '@ngui/web/ngui-card.js');
```

Error: `InternalError: module record has unexpected status: New`

**The Solution:**

We bypass Vite entirely by injecting `<script type="module">` tags with inline import statements. This forces the browser to use its native importmap resolution:

```javascript
// ✅ Browser handles this via importmap
const script = document.createElement('script');
script.type = 'module';
script.textContent = `import '@ngui/web/ngui-card.js';`;
document.head.appendChild(script);
```

See `client/src/utils/loadWebComponents.ts:32-63` for the full implementation.

**Why This Approach:**
- Vite's module resolution is incompatible with runtime importmap usage
- Static import paths are required (no dynamic variables)
- Switch statement with hardcoded import strings ensures proper resolution
- Script tag injection completely bypasses Vite's module interceptor

### Import Map Configuration

The client's `index.html` defines the import map:

```html
<script type="importmap">
  {
    "imports": {
      "lit": "https://cdn.jsdelivr.net/npm/lit@3.2.1/+esm",
      "lit/": "https://cdn.jsdelivr.net/npm/lit@3.2.1/",
      "@patternfly/elements/": "https://cdn.jsdelivr.net/npm/@patternfly/elements@3.0.0/",
      "@rhngui/web/": "/ngui-elements/"
    }
  }
</script>
```

The `@rhngui/web/` prefix maps to `/ngui-elements/`. During development, Vite's middleware intercepts these requests and serves the TypeScript sources directly. In production, the built JavaScript files are served from the `public/` directory.

## Development

### Development Workflow

**Initial Setup:**
```bash
cd libs/next_gen_ui_web
npm install
```

**Development Mode:**

Vite serves the TypeScript sources directly during development - no build step needed!

```bash
# Terminal 1: Run e2e test server (if testing backend integration)
cd tests/ngui-e2e/server
# <run server command>

# Terminal 2: Run client dev server
cd tests/ngui-e2e/client
npm run dev
```

Edit web component source files in `libs/next_gen_ui_web/elements/` and Vite will automatically recompile and hot reload!

**Production Build:**

Only needed when building for production or testing the actual build output:

```bash
cd libs/next_gen_ui_web
npm run build  # Compiles TS, generates manifest, copies to client public/
```

### Vite Configuration

The e2e client's Vite config includes:
- **Custom middleware** - Intercepts `/ngui-elements/*.js` requests and rewrites to TypeScript sources during dev
- **Aliases** - `@rhngui/web/ngui-card.js` → `libs/next_gen_ui_web/elements/ngui-card.ts` (serves TypeScript sources in dev)
- **optimizeDeps.exclude** - Prevents pre-bundling of `@rhngui/web` to preserve import map resolution at runtime
- **server.fs.allow** - Allows serving files from the project root to access web component sources

## Resources

- [Lit Documentation](https://lit.dev/)
- [PatternFly Elements](https://github.com/patternfly/patternfly-elements)
- [PatternFly v6 Design Tokens](https://www.patternfly.org/tokens/all-patternfly-tokens/)
- [Custom Elements Manifest](https://custom-elements-manifest.open-wc.org/)
- [Import Maps](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap)

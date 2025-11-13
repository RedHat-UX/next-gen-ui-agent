/// <reference types="react" />

declare namespace JSX {
  interface IntrinsicElements {
    "ngui-card": React.DetailedHTMLProps<
      React.HTMLAttributes<HTMLElement> & {
        title?: string;
      },
      HTMLElement
    >;
  }
}

declare module "@rhngui/web/elements/index.js" {
  export class NguiCard extends HTMLElement {}
}

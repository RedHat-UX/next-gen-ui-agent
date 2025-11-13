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

declare module "ngui-web-components/elements/index.js" {
  export class NguiCard extends HTMLElement {}
}

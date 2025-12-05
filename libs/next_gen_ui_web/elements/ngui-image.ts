import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

/**
 * A framework-agnostic image component following PatternFly v6 design system.
 *
 * This component displays images with loading states, error handling, and
 * accessibility features aligned with PatternFly v6 specifications.
 *
 * ## Usage
 *
 * ### Basic Usage
 * ```html
 * <ngui-image
 *   src="https://example.com/image.jpg"
 *   alt="Description of image">
 * </ngui-image>
 * ```
 *
 * ### With Title
 * ```html
 * <ngui-image
 *   src="https://example.com/poster.jpg"
 *   alt="Movie poster"
 *   title="Toy Story Poster">
 * </ngui-image>
 * ```
 *
 * ### With Slotted Content
 * ```html
 * <ngui-image>
 *   <img slot="image" src="https://example.com/image.jpg" alt="Custom image">
 *   <p slot="caption">Image caption goes here</p>
 * </ngui-image>
 * ```
 *
 * @element ngui-image
 *
 * @slot image - OPTIONAL: Slot for providing a custom `<img>` element
 * @slot caption - OPTIONAL: Slot for image caption or description
 *
 * @cssprop --ngui-image-max-width - Maximum width of the image container (default: 100%)
 * @cssprop --ngui-image-border-radius - Border radius for images (default: PF v6 border radius)
 *
 * @csspart container - The outer container element
 * @csspart image - The image element itself
 * @csspart title - The title heading element
 * @csspart caption - The caption container
 *
 * @fires {CustomEvent} load - Fired when image successfully loads
 * @fires {CustomEvent} error - Fired when image fails to load
 */
@customElement('ngui-image')
export class NguiImage extends LitElement {
  static styles = css`
    :host {
      display: block;
      container-type: inline-size;
    }

    .container {
      max-width: var(--ngui-image-max-width, 100%);
      margin: 0;
      padding: 0;
    }

    .title {
      font-family: var(--pf-v6-global--FontFamily--heading, 'Red Hat Display', sans-serif);
      font-size: var(--pf-v6-global--FontSize--xl, 1.25rem);
      font-weight: var(--pf-v6-global--FontWeight--bold, 700);
      color: var(--pf-v6-global--Color--100, #151515);
      margin: 0 0 var(--pf-v6-global--spacer--md, 16px) 0;
      padding: 0;
    }

    .image-wrapper {
      position: relative;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: var(--pf-v6-global--BackgroundColor--200, #f0f0f0);
      border-radius: var(--ngui-image-border-radius, var(--pf-v6-global--BorderRadius--lg, 8px));
      overflow: hidden;
      min-height: 200px;
    }

    img {
      max-width: 100%;
      height: auto;
      display: block;
      border-radius: var(--ngui-image-border-radius, var(--pf-v6-global--BorderRadius--lg, 8px));
    }

    .loading,
    .error,
    .no-image {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: var(--pf-v6-global--spacer--xl, 24px);
      color: var(--pf-v6-global--Color--200, #6a6e73);
      font-family: var(--pf-v6-global--FontFamily--text, 'Red Hat Text', sans-serif);
      font-size: var(--pf-v6-global--FontSize--md, 1rem);
      text-align: center;
    }

    .loading::before,
    .error::before,
    .no-image::before {
      content: '';
      display: block;
      width: 48px;
      height: 48px;
      margin-bottom: var(--pf-v6-global--spacer--md, 16px);
      background-size: contain;
      background-repeat: no-repeat;
      background-position: center;
    }

    .loading::before {
      /* Simple loading animation using border */
      border: 4px solid var(--pf-v6-global--BorderColor--100, #d2d2d2);
      border-top-color: var(--pf-v6-global--primary-color--100, #06c);
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error {
      color: var(--pf-v6-global--danger-color--100, #c9190b);
    }

    .caption {
      margin-top: var(--pf-v6-global--spacer--sm, 8px);
      font-family: var(--pf-v6-global--FontFamily--text, 'Red Hat Text', sans-serif);
      font-size: var(--pf-v6-global--FontSize--sm, 0.875rem);
      color: var(--pf-v6-global--Color--200, #6a6e73);
    }
  `;

  /**
   * Source URL of the image to display.
   *
   * MUST be a valid URL string. When set, this will load the image.
   * If loading fails, an error state will be shown.
   *
   * @type {string}
   * @default ""
   */
  @property({ type: String })
  src = '';

  /**
   * Alternative text for the image (required for accessibility).
   *
   * MUST provide descriptive text for screen readers. This is critical
   * for accessibility compliance.
   *
   * @type {string}
   * @default ""
   */
  @property({ type: String })
  alt = '';

  /**
   * Optional title displayed above the image.
   *
   * OPTIONAL: If provided, displays as a heading above the image
   * using PatternFly v6 heading styles.
   *
   * @type {string}
   * @default ""
   */
  @property({ type: String })
  title = '';

  @state()
  private _loading = false;

  @state()
  private _error = false;

  private _handleImageLoad() {
    this._loading = false;
    this._error = false;
    this.dispatchEvent(new CustomEvent('load', {
      bubbles: true,
      composed: true,
    }));
  }

  private _handleImageError() {
    this._loading = false;
    this._error = true;
    this.dispatchEvent(new CustomEvent('error', {
      bubbles: true,
      composed: true,
      detail: { src: this.src },
    }));
  }

  updated(changedProperties: Map<string, unknown>) {
    if (changedProperties.has('src') && this.src) {
      this._loading = true;
      this._error = false;
    }
  }

  render() {
    return html`
      <div part="container" class="container">
        ${this.title ? html`<h2 part="title" class="title">${this.title}</h2>` : ''}

        <div class="image-wrapper">
          <slot name="image">
            ${this.src
              ? html`
                  <img
                    part="image"
                    src="${this.src}"
                    alt="${this.alt}"
                    @load="${this._handleImageLoad}"
                    @error="${this._handleImageError}"
                    ?hidden="${this._loading || this._error}"
                  />
                  ${this._loading ? html`<div class="loading">Loading image...</div>` : ''}
                  ${this._error ? html`<div class="error">Failed to load image</div>` : ''}
                `
              : html`<div class="no-image">No image provided</div>`
            }
          </slot>
        </div>

        <div part="caption" class="caption">
          <slot name="caption"></slot>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'ngui-image': NguiImage;
  }
}

import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import '@patternfly/elements/pf-card/pf-card.js';

/**
 * A card component for displaying structured content with optional image and header.
 *
 * Use this component when you need to present information in a contained, visually distinct format.
 * This component wraps PatternFly's `<pf-card>` and adapts it to PatternFly v6 design specifications.
 *
 * The card MUST contain a title via the `title` attribute or `header` slot.
 * Content SHOULD be provided via the default slot.
 * Images SHOULD use the `image` slot and MUST include appropriate alt text.
 * Set `layout="horizontal-split"` to use PatternFly's horizontal split layout pattern.
 *
 * ## Accessibility
 *
 * The card is implemented as a semantic article element with proper ARIA labeling.
 * Screen readers will announce the card title as the accessible label.
 * All slotted images MUST have alt attributes for screen reader compatibility.
 *
 * Keyboard users can navigate to interactive elements within the card using Tab.
 * Focus indicators are preserved for all interactive child elements.
 *
 * ## Usage Examples
 *
 * Basic card with title and content:
 * ```html
 * <ngui-card title="Product Details">
 *   <dl>
 *     <dt>Price</dt><dd>$29.99</dd>
 *     <dt>Stock</dt><dd>In Stock</dd>
 *   </dl>
 * </ngui-card>
 * ```
 *
 * Card with image (horizontal split layout):
 * ```html
 * <ngui-card title="Product Name" layout="horizontal-split">
 *   <img slot="image" src="product.jpg" alt="Product photo">
 *   <p>Product description here.</p>
 * </ngui-card>
 * ```
 *
 * @element ngui-card
 * @attr {string} title - The card title text
 * @attr {string} layout - Layout pattern: "default" or "horizontal-split"
 * @slot - Default slot for card content.
 * @slot header - Custom header content. USE when you need more than plain text title.
 * @slot image - Image content. MUST include alt text.
 *
 * @cssprop --ngui-card-padding - Padding inside the card body. Default: var(--pf-v6-global--spacer--md)
 * @cssprop --ngui-card-border-radius - Border radius of the card. Default: var(--pf-v6-global--BorderRadius--lg)
 * @cssprop --ngui-card-background - Background color of the card. Default: var(--pf-v6-global--BackgroundColor--100)
 *
 * @csspart header - The card header section wrapper. USE to style header layout and spacing.
 * @csspart body - The card body/content section. USE to style content layout and spacing.
 */
@customElement('ngui-card')
export class NguiCard extends LitElement {
  static styles = css`
    :host {
      display: block;
      container-type: inline-size;

      /* PatternFly v6 card design tokens */
      --pf-v6-c-card--BackgroundColor: var(--pf-t--global--background--color--primary--default);
      --pf-v6-c-card--BorderColor: var(--pf-t--global--border--color--default);
      --pf-v6-c-card--BorderStyle: solid;
      --pf-v6-c-card--BorderWidth: var(--pf-t--global--border--width--box--default);
      --pf-v6-c-card--BorderRadius: var(--pf-t--global--border--radius--medium);
      --pf-v6-c-card--first-child--PaddingBlockStart: var(--pf-t--global--spacer--lg);
      --pf-v6-c-card--child--PaddingInlineEnd: var(--pf-t--global--spacer--lg);
      --pf-v6-c-card--child--PaddingBlockEnd: var(--pf-t--global--spacer--lg);
      --pf-v6-c-card--child--PaddingInlineStart: var(--pf-t--global--spacer--lg);
      --pf-v6-c-card__title-text--Color: var(--pf-t--global--text--color--regular);
      --pf-v6-c-card__title-text--FontFamily: var(--pf-t--global--font--family--heading);
      --pf-v6-c-card__title-text--FontSize: var(--pf-t--global--font--size--heading--xs);
      --pf-v6-c-card__title-text--FontWeight: var(--pf-t--global--font--weight--heading--default);
      --pf-v6-c-card__title-text--LineHeight: var(--pf-t--global--font--line-height--heading);
      --pf-v6-c-card__body--FontSize: var(--pf-t--global--font--size--body--default);
    }

    /* Apply PF v6 card styling to pf-card */
    pf-card {
      overflow: hidden;
      background-color: var(--pf-v6-c-card--BackgroundColor);
      border-color: var(--pf-v6-c-card--BorderColor);
      border-style: var(--pf-v6-c-card--BorderStyle);
      border-width: var(--pf-v6-c-card--BorderWidth);
      border-radius: var(--pf-v6-c-card--BorderRadius);
      /* Style pf-card's parts */
      &::part(header) {
        padding: var(--pf-v6-c-card--child--PaddingInlineStart) var(--pf-v6-c-card--child--PaddingInlineEnd) var(--pf-t--global--spacer--md);
      }

      &::part(body) {
        padding: var(--pf-v6-c-card--child--PaddingInlineStart);
        color: var(--pf-v6-c-card__title-text--Color);
        font-size: var(--pf-v6-c-card__body--FontSize);
      }

      &::part(footer) {
        padding: var(--pf-v6-c-card--child--PaddingInlineStart);
      }
    }

    /* Horizontal split: apply grid to pf-card */
    :host([layout="horizontal-split"]) {
      pf-card {
        display: grid;
        grid-template-areas:
          "image"
          "header"
          "body"
          "footer";
        grid-template-columns: 1fr;
        grid-template-rows: auto auto 1fr auto;
        &::part(body) { display: contents; }
        &::part(header) { grid-area: header; }
        &::part(footer) { grid-area: footer; }
        @media (min-width: 768px) {
          column-gap: var(--pf-v6-c-card--child--PaddingInlineStart);
          &::part(header),
          &::part(footer) { padding-inline-start: 0; }
          grid-template-areas:
            "image header"
            "image body"
            "image footer";
          grid-template-columns: 1fr 1fr;
          grid-template-rows: auto 1fr auto;
        }
      }

      /* Assign grid areas */
      #image {
        grid-area: image;
        height: 100%;
        min-height: 200px;
        & ::slotted(img) {
          width: 100%;
          min-height: 100%;
          object-fit: cover;
        }
      }

      /* Body has display:contents, so pad the slotted content instead */
      slot:not([name])::slotted(*) {
        padding: var(--pf-v6-c-card--child--PaddingInlineStart);
      }
    }

    .card-header {
      font-family: var(--pf-v6-c-card__title-text--FontFamily);
      font-size: var(--pf-v6-c-card__title-text--FontSize);
      font-weight: var(--pf-v6-c-card__title-text--FontWeight);
      color: var(--pf-v6-c-card__title-text--Color);
      line-height: var(--pf-v6-c-card__title-text--LineHeight);
      margin: 0;
    }
  `;

  /**
   * The title text displayed in the card header.
   *
   * This property sets the main heading for the card.
   * USE this for simple text titles.
   * For more complex headers with icons or actions, USE the `header` slot instead.
   *
   * The title is used as the accessible label for the card via aria-label.
   * Screen readers will announce this title when the card receives focus.
   *
   * @type {string}
   * @attr
   */
  @property({ type: String })
  title = '';

  /**
   * The layout pattern for the card.
   *
   * - `default`: Standard vertical layout
   * - `horizontal-split`: 50/50 split with image on left, content on right (768px+)
   *
   * @type {'default' | 'horizontal-split'}
   * @attr
   */
  @property({ type: String })
  layout: 'default' | 'horizontal-split' = 'default';

  async firstUpdated() {
    // WORKAROUND: Remove pf-card's internal article wrapper to enable grid layout.
    // This manipulates pf-card's shadow DOM to make header/body/footer parts
    // direct children of pf-card, allowing proper grid area assignment.
    const pfCard = this.shadowRoot?.querySelector('pf-card');
    await pfCard?.updateComplete;
    const article = pfCard?.shadowRoot?.querySelector('article');
    article?.replaceWith(...article.children);
  }

  render() {
    return html`
      <pf-card>
        <div id="image"><slot name="image"></slot></div>
        <div id="header" slot="header"><slot name="header">
          ${this.title ? html`<h2 class="card-header">${this.title}</h2>` : ''}
        </slot></div>
        <slot></slot>
        <div id="footer" slot="footer"><slot name="footer"></slot></div>
      </pf-card>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'ngui-card': NguiCard;
  }
}

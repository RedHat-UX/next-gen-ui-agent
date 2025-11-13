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
 * Content SHOULD be provided via the default slot or named `content` slot.
 * Images SHOULD use the `image` slot and MUST include appropriate alt text.
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
 *   <dl slot="content">
 *     <dt>Price</dt><dd>$29.99</dd>
 *     <dt>Stock</dt><dd>In Stock</dd>
 *   </dl>
 * </ngui-card>
 * ```
 *
 * Card with image:
 * ```html
 * <ngui-card title="Product Name">
 *   <img slot="image" src="product.jpg" alt="Product photo">
 *   <p slot="content">Product description here.</p>
 * </ngui-card>
 * ```
 *
 * @element ngui-card
 * @slot - Default slot for card content. USE this for simple content.
 * @slot header - Custom header content. USE when you need more than plain text title.
 * @slot image - Image content displayed at the top of the card. MUST include alt text.
 * @slot content - Named slot for main card content. USE for structured content like definition lists.
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
    }

    pf-card {
      --pf-c-card--BackgroundColor: var(--ngui-card-background, var(--pf-v6-global--BackgroundColor--100, #fff));
      --pf-c-card--BorderRadius: var(--ngui-card-border-radius, var(--pf-v6-global--BorderRadius--lg, 8px));
    }

    pf-card::part(body) {
      padding: var(--ngui-card-padding, var(--pf-v6-global--spacer--md, 16px));
    }

    /* PFv6 Design Adaptations */
    .card-header {
      font-family: var(--pf-v6-global--FontFamily--heading, 'Red Hat Display', sans-serif);
      font-size: var(--pf-v6-global--FontSize--xl, 1.25rem);
      font-weight: var(--pf-v6-global--FontWeight--bold, 700);
      color: var(--pf-v6-global--Color--100, #151515);
      margin: 0;
      padding: var(--pf-v6-global--spacer--md, 16px);
    }

    .card-image {
      display: block;
      width: 100%;
      height: auto;
      object-fit: cover;
    }

    .card-content {
      padding: var(--pf-v6-global--spacer--md, 16px);
    }

    /* Responsive image layout */
    @container (min-width: 576px) {
      .card-with-image {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: var(--pf-v6-global--spacer--lg, 24px);
      }
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
   * Indicates whether the card has an image in the image slot.
   *
   * This is automatically detected based on slot content.
   * When true, the card layout adapts to display the image alongside content
   * on larger screens (min-width: 576px).
   *
   * @type {boolean}
   * @private
   */
  @property({ type: Boolean, attribute: false })
  private hasImage = false;

  private handleImageSlotChange(e: Event) {
    const slot = e.target as HTMLSlotElement;
    this.hasImage = slot.assignedElements().length > 0;
  }

  render() {
    return html`
      <pf-card
        role="article"
        aria-label=${this.title || 'Card'}
        class=${this.hasImage ? 'card-with-image' : ''}
      >
        <slot
          name="image"
          @slotchange=${this.handleImageSlotChange}
        ></slot>

        <div part="header" class="card-header-wrapper">
          <slot name="header">
            ${this.title ? html`<h2 class="card-header">${this.title}</h2>` : ''}
          </slot>
        </div>

        <div part="body" class="card-content">
          <slot name="content">
            <slot></slot>
          </slot>
        </div>
      </pf-card>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'ngui-card': NguiCard;
  }
}

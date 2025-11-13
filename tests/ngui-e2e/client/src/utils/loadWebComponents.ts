/**
 * Dynamically loads web components found in HTML string
 *
 * This function parses HTML to find all custom elements with the `ngui-` prefix
 * and dynamically loads only the component modules needed for that HTML.
 * Uses script tags to bypass Vite and load via browser's native importmap.
 *
 * @param html - HTML string containing custom elements
 * @returns Promise that resolves when all required components are loaded
 *
 * @example
 * const html = '<ngui-card title="Test"><p>Content</p></ngui-card>';
 * await loadWebComponents(html);
 * // ngui-card is now defined and ready to use
 */
export async function loadWebComponents(html: string): Promise<void> {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');

  // Find all ngui-* custom elements
  const allElements = doc.querySelectorAll('*');
  const tagNames = new Set<string>();

  allElements.forEach(el => {
    const tagName = el.tagName.toLowerCase();
    if (tagName.startsWith('ngui-')) {
      tagNames.add(tagName);
    }
  });

  // Load components using script tags to bypass Vite and use importmap
  const loadPromises = Array.from(tagNames).map((tagName) => {
    // Check if already defined
    if (customElements.get(tagName)) {
      return Promise.resolve();
    }

    const modulePath = tagName.replace('ngui-', '');

    return new Promise<void>((resolve, reject) => {
      const script = document.createElement('script');
      script.type = 'module';

      switch (tagName) {
        case 'ngui-card':
          script.textContent = `import '@ngui/web/ngui-card.js';`;
          break;
        case 'ngui-image':
          script.textContent = `import '@ngui/web/ngui-image.js';`;
          break;
        default:
          reject(new Error(`Unknown web component: ${tagName}`));
          return;
      }

      script.onload = () => {
        // Wait for custom element to be defined
        customElements.whenDefined(tagName).then(() => resolve());
      };
      script.onerror = () => reject(new Error(`Failed to load ${tagName}`));

      document.head.appendChild(script);
    });
  });

  await Promise.all(loadPromises);
}

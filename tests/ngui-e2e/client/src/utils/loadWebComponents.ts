/**
 * Dynamically loads web components found in HTML string
 *
 * This function parses HTML to find all custom elements with the `ngui-` prefix
 * and dynamically imports only the component modules needed for that HTML.
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

  // Dynamically import only the components found in this HTML
  const imports = Array.from(tagNames).map(tagName =>
    import(`/ngui-elements/${tagName}.js`)
  );

  await Promise.all(imports);
}

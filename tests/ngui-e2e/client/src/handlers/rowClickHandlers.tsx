import type { ComponentHandlerRegistry } from '@rhngui/patternfly-react-renderer';
import { triggerPrompt } from './promptTrigger';

/**
 * Type for row data passed to onRowClick handlers
 */
export type RowData = Record<string, unknown>;

/**
 * Type for onRowClick handler function
 */
export type RowClickHandler = (event: React.MouseEvent, rowData: RowData) => void;

/**
 * Global handler map for row click handlers
 * The renderer will look up handlers by ID from this map
 */
export const ROW_CLICK_HANDLERS: Map<string, RowClickHandler> = new Map();

/**
 * Helper to get a value from rowData by trying multiple possible keys (case-insensitive)
 */
const getRowValue = (rowData: RowData, ...keys: string[]): unknown => {
  for (const key of keys) {
    // Try exact match
    if (key in rowData) {
      return rowData[key];
    }
    // Try case-insensitive match
    const lowerKey = key.toLowerCase();
    for (const rowKey in rowData) {
      if (rowKey.toLowerCase() === lowerKey) {
        return rowData[rowKey];
      }
    }
  }
  return undefined;
};

/**
 * Handler for OpenShift pods - displays detailed information and triggers a prompt
 */
const podsHandler: RowClickHandler = (event, rowData) => {
  event.preventDefault();
  
  // Debug: log the actual rowData keys
  console.log('[Pods Handler] Row data keys:', Object.keys(rowData));
  console.log('[Pods Handler] Row data:', rowData);
  
  // Try multiple possible key names (display names vs field names)
  const name = getRowValue(rowData, 'name', 'Name') || 'N/A';
  const namespace = getRowValue(rowData, 'namespace', 'Namespace') || 'N/A';
  
  // Build a prompt asking for more details about this specific pod
  const podName = name !== 'N/A' ? name : 'this pod';
  const prompt = `Show me detailed information about pod ${podName}${namespace !== 'N/A' ? ` in namespace ${namespace}` : ''}`;
  
  // Trigger the prompt with a specific tool for detailed pod information
  triggerPrompt(prompt, undefined, undefined, 'get_openshift_pod_details');
};

/**
 * Handler for OpenShift nodes - displays detailed information and triggers a prompt
 */
const nodesHandler: RowClickHandler = (event, rowData) => {
  event.preventDefault();
  
  // Debug: log the actual rowData keys
  console.log('[Nodes Handler] Row data keys:', Object.keys(rowData));
  console.log('[Nodes Handler] Row data:', rowData);
  
  // Try multiple possible key names (display names vs field names)
  const name = getRowValue(rowData, 'name', 'Name') || 'N/A';
  
  // Build a prompt asking for more details about this specific node
  const nodeName = name !== 'N/A' ? name : 'this node';
  const prompt = `Show me detailed information about node ${nodeName}`;
  
  // Trigger the prompt with a specific tool for detailed node information
  triggerPrompt(prompt, undefined, undefined, 'get_openshift_node_details');
};

/**
 * Generic products handler - shows a browser alert with product details
 * This is registered as a generic "onRowClick" handler that can be used by any data type
 */
const productsHandler: RowClickHandler = (event, rowData) => {
  event.preventDefault();
  
  console.log('[Products Handler] Row data keys:', Object.keys(rowData));
  console.log('[Products Handler] Row data:', rowData);
  
  // Extract product information
  const name = String(getRowValue(rowData, 'name', 'Name') || 'Unknown Product');
  const price = getRowValue(rowData, 'price', 'Price');
  const status = String(getRowValue(rowData, 'status', 'Status') || 'Unknown');
  
  // Format price if it's a number
  const formattedPrice = typeof price === 'number' 
    ? `$${price.toFixed(2)}` 
    : String(price || 'N/A');
  
  // Show browser alert with product details
  const message = `Product Details\n\nName: ${name}\nPrice: ${formattedPrice}\nStatus: ${status}`;
  window.alert(message);
};

/**
 * Registers onRowClick handlers for OpenShift pods and nodes.
 * These handlers display detailed information when a row is clicked.
 * 
 * The renderer may use getFormatter to resolve handlers, so we register them
 * both via registerOnRowClick (if available) and as formatters as a fallback.
 * 
 * @param registry - The ComponentHandlerRegistry instance to register handlers with
 * @returns Array of registered handler IDs
 */
export function registerRowClickHandlers(registry: ComponentHandlerRegistry): string[] {
  const registeredIds: string[] = [];

  // Store handlers in global map for direct access if needed
  ROW_CLICK_HANDLERS.set('get_openshift_pods.onRowClick', podsHandler);
  ROW_CLICK_HANDLERS.set('get_openshift_nodes.onRowClick', nodesHandler);
  ROW_CLICK_HANDLERS.set('onRowClick', productsHandler); // Generic handler for products and other data types
  
  // Register handlers using registerOnRowClick method (preferred method)
  if ('registerOnRowClick' in registry && typeof (registry as any).registerOnRowClick === 'function') {
    (registry as any).registerOnRowClick('get_openshift_pods.onRowClick', podsHandler);
    (registry as any).registerOnRowClick('get_openshift_nodes.onRowClick', nodesHandler);
    (registry as any).registerOnRowClick('onRowClick', productsHandler); // Generic handler
    console.log('[Handlers] Registered row click handlers via registerOnRowClick');
  } else {
    console.warn('[Handlers] registerOnRowClick method not found, trying alternative registration');
  }

  // The renderer uses getFormatter to resolve handlers, so we need to register them there too
  // But we need to make sure the renderer knows these are handlers, not formatters
  // The renderer should check registerOnRowClick first, but if it falls back to getFormatter,
  // we need to ensure the handler is available there
  if ('registerFormatter' in registry && typeof registry.registerFormatter === 'function') {
    // Register as formatters so getFormatter can find them
    // The renderer will call them with (event, rowData) when used as handlers
    registry.registerFormatter('get_openshift_pods.onRowClick', podsHandler as any);
    registry.registerFormatter('get_openshift_nodes.onRowClick', nodesHandler as any);
    registry.registerFormatter('onRowClick', productsHandler as any); // Generic handler
    console.log('[Handlers] Also registered handlers as formatters (for getFormatter lookup)');
  }

  registeredIds.push('get_openshift_pods.onRowClick', 'get_openshift_nodes.onRowClick', 'onRowClick');
  console.log('[Handlers] Registered handler IDs:', registeredIds);
  
  // Debug: Check if handlers can be retrieved via different methods
  if ('getFormatter' in registry && typeof (registry as any).getFormatter === 'function') {
    const podsHandlerRetrieved = (registry as any).getFormatter('get_openshift_pods.onRowClick');
    const nodesHandlerRetrieved = (registry as any).getFormatter('get_openshift_nodes.onRowClick');
    console.log('[Handlers] Debug - Can retrieve pods handler via getFormatter?', typeof podsHandlerRetrieved === 'function');
    console.log('[Handlers] Debug - Can retrieve nodes handler via getFormatter?', typeof nodesHandlerRetrieved === 'function');
  }
  
  // Check if there's a getOnRowClick method
  if ('getOnRowClick' in registry && typeof (registry as any).getOnRowClick === 'function') {
    const podsHandlerRetrieved = (registry as any).getOnRowClick('get_openshift_pods.onRowClick');
    const nodesHandlerRetrieved = (registry as any).getOnRowClick('get_openshift_nodes.onRowClick');
    console.log('[Handlers] Debug - Can retrieve pods handler via getOnRowClick?', typeof podsHandlerRetrieved === 'function');
    console.log('[Handlers] Debug - Can retrieve nodes handler via getOnRowClick?', typeof nodesHandlerRetrieved === 'function');
  } else {
    console.log('[Handlers] Debug - getOnRowClick method not found on registry');
  }
  
  // Log all available methods on the registry for debugging
  console.log('[Handlers] Debug - Registry methods:', Object.keys(registry).filter(key => typeof (registry as any)[key] === 'function'));

  return registeredIds;
}

/**
 * Gets a row click handler by ID
 */
export function getRowClickHandler(handlerId: string): RowClickHandler | undefined {
  return ROW_CLICK_HANDLERS.get(handlerId);
}


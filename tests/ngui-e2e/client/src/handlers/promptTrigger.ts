/**
 * Global callback for triggering prompts from row click handlers
 * This allows handlers to send follow-up prompts to the chatbot
 */
let promptTriggerCallback: ((prompt: string, dataset?: string, datasetType?: string, toolName?: string) => void) | null = null;

/**
 * Register a callback function that will be called when a handler wants to trigger a prompt
 */
export function registerPromptTrigger(
  callback: (prompt: string, dataset?: string, datasetType?: string, toolName?: string) => void
): () => void {
  promptTriggerCallback = callback;
  // Return cleanup function
  return () => {
    promptTriggerCallback = null;
  };
}

/**
 * Trigger a prompt from a handler
 * This will call the registered callback if available
 * 
 * @param prompt - The prompt text to send
 * @param dataset - Optional dataset to attach (defaults to current dataset)
 * @param datasetType - Optional dataset type (defaults to current dataset type)
 * @param toolName - Optional tool name to use (overrides dataset type for tool selection)
 */
export function triggerPrompt(
  prompt: string,
  dataset?: string,
  datasetType?: string,
  toolName?: string
): void {
  if (promptTriggerCallback) {
    promptTriggerCallback(prompt, dataset, datasetType, toolName);
  } else {
    console.warn('[PromptTrigger] No callback registered. Prompt not sent:', prompt);
  }
}


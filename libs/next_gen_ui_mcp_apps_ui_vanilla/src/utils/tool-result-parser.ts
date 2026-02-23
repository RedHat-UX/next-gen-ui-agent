import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import type { MCPGenerateUIOutput } from "./types.js";

export interface ToolResultParserResult {
  /** HTML content strings from blocks with mime_type text/html (RHDS renderer). */
  htmlContents: string[];
  error: string | null;
  isLoading: boolean;
}

/**
 * Parses MCP tool result into HTML contents produced by next_gen_ui_rhds_renderer.
 *
 * The server-side next_gen_ui_rhds_renderer (--component-system rhds) outputs
 * UIBlock.rendering with mime_type "text/html" and content = HTML string (RHDS
 * web components: rh-card, rh-table, etc.). This parser extracts those HTML
 * strings for the vanilla app to inject into the DOM.
 */
export function parseToolResult(toolResult: CallToolResult | null): ToolResultParserResult {
  if (!toolResult) {
    return { htmlContents: [], error: null, isLoading: true };
  }

  try {
    const structuredContent =
      (toolResult as { structuredContent?: unknown }).structuredContent ??
      (toolResult as { structured_content?: unknown }).structured_content;

    let output: MCPGenerateUIOutput;

    if (structuredContent && typeof structuredContent === "object") {
      output = structuredContent as MCPGenerateUIOutput;
    } else if (Array.isArray(toolResult.content) && toolResult.content[0]) {
      const firstContent = toolResult.content[0];
      if (
        firstContent &&
        typeof firstContent === "object" &&
        (firstContent as { type?: string }).type === "text"
      ) {
        const textContent = (firstContent as { text?: string }).text;
        if (typeof textContent !== "string") {
          throw new Error("Missing text content");
        }
        output = JSON.parse(textContent) as MCPGenerateUIOutput;
      } else {
        throw new Error(
          `Unsupported content type: ${(firstContent as { type?: string })?.type ?? "unknown"}`
        );
      }
    } else {
      throw new Error("No tool result data available");
    }

    const htmlContents = (output.blocks ?? [])
      .filter(
        (block) =>
          block.rendering?.content && block.rendering.mime_type === "text/html"
      )
      .map((block) => block.rendering!.content as string);

    return { htmlContents, error: null, isLoading: false };
  } catch (e) {
    console.error("Error processing tool result:", e);
    return {
      htmlContents: [],
      error: e instanceof Error ? e.message : String(e),
      isLoading: false,
    };
  }
}

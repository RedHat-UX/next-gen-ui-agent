import { useEffect, useState } from "react";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import type { MCPGenerateUIOutput } from "./types";

interface UseToolResultParserResult {
  componentConfigs: any[];
  error: string | null;
  isLoading: boolean;
}

export function useToolResultParser(toolResult: CallToolResult | null): UseToolResultParserResult {
  const [componentConfigs, setComponentConfigs] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!toolResult) {
      return;
    }

    try {
      // Debug: Log the tool result structure
      console.log("Tool result received:", {
        hasStructuredContent: !!toolResult.structured_content,
        hasContent: !!toolResult.content,
        contentLength: toolResult.content?.length,
        structuredContentKeys: toolResult.structured_content ? Object.keys(toolResult.structured_content) : [],
        firstContentType: toolResult.content?.[0]?.type,
        fullToolResult: toolResult,
      });

      // Parse the tool result to get the MCPGenerateUIOutput
      let output: MCPGenerateUIOutput;

      // Check for structuredContent (camelCase) or structured_content (snake_case)
      const structuredContent = toolResult.structuredContent || toolResult.structured_content;

      if (structuredContent) {
        // Structured content is already an object
        console.log("Using structured content:", structuredContent);
        output = structuredContent as MCPGenerateUIOutput;
      } else if (toolResult.content?.[0]) {
        // Parse JSON from text content
        const firstContent = toolResult.content[0];
        if (firstContent.type === "text") {
          const textContent = firstContent.text;
          try {
            output = JSON.parse(textContent);
          } catch (parseError) {
            // If JSON parsing fails, show the actual content in the error
            console.error("Failed to parse tool result. Content:", textContent);
            throw new Error(`Invalid JSON response from server: ${textContent.substring(0, 200)}...`);
          }
        } else {
          throw new Error(`Unsupported content type: ${firstContent.type}`);
        }
      } else {
        throw new Error("No tool result data available");
      }

      // Extract component configs from UIBlocks
      const configs = output.blocks
        .filter((block) => block.rendering?.content)
        .map((block) => {
          try {
            return JSON.parse(block.rendering!.content);
          } catch (e) {
            console.error("Failed to parse component config:", e);
            return null;
          }
        })
        .filter(Boolean);

      setComponentConfigs(configs);
      setError(null);
      setIsLoading(false);
    } catch (e) {
      console.error("Error processing tool result:", e);
      setError(e instanceof Error ? e.message : String(e));
      setIsLoading(false);
    }
  }, [toolResult]);

  return { componentConfigs, error, isLoading };
}

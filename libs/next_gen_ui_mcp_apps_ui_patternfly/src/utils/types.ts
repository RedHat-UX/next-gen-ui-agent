export interface UIBlock {
  id: string;
  rendering?: {
    id: string;
    component_system: string;
    mime_type: string;
    content: string; // JSON string of component config
  };
  configuration?: any;
}

export interface MCPGenerateUIOutput {
  blocks: UIBlock[];
  summary: string;
}

export interface ToolResultContent {
  text?: string;
  type?: string;
}

export interface ToolResult {
  content?: ToolResultContent[];
  structuredContent?: any; // Note: camelCase in MCP protocol
  structured_content?: any; // Keep for backward compatibility
}

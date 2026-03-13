export interface UIBlock {
  id: string;
  rendering?: {
    id: string;
    component_system: string;
    mime_type: string;
    content: string;
  };
  configuration?: unknown;
}

export interface MCPGenerateUIOutput {
  blocks: UIBlock[];
  summary: string;
}

export interface TrustedHtml {
  trusted: boolean;
  value: string;
}

import React, { useState } from 'react';
import { Button } from '@patternfly/react-core';
import { MetadataViewer } from './MetadataViewer';
import { PipelineViewer } from './PipelineViewer';
import { DataTransformationViewer } from './DataTransformationViewer';
import { JsonViewer } from './JsonViewer';

interface DebugSectionProps {
  metadata?: {
    componentType?: string;
    reason?: string;
    confidence?: string;
    strategy?: string;
  };
  llmInteractions?: Array<{
    step: string;
    system_prompt: string;
    user_prompt: string;
    raw_response: string;
  }>;
  agentMessages?: Array<{
    type: string;
    content: string;
    tool_calls?: Array<{ name: string; args: Record<string, unknown> }>;
    name?: string;
  }>;
  dataTransform?: {
    transformerName?: string;
    jsonWrappingField?: string;
    fieldCount?: number;
    fields?: Array<{
      name: string;
      dataPath: string;
    }>;
  };
  config?: any;
  messageId: string;
}

export function DebugSection({ 
  metadata, 
  llmInteractions, 
  agentMessages, 
  dataTransform,
  config,
  messageId 
}: DebugSectionProps) {
  const [openSection, setOpenSection] = useState<'debug' | 'json' | null>(null);

  const toggleSection = (section: 'debug' | 'json') => {
    setOpenSection(prev => prev === section ? null : section);
  };

  return (
    <div className="debug-section-container">
      <div className="debug-section-buttons">
        <Button 
          variant="link" 
          onClick={() => toggleSection('debug')}
          className="debug-section-button"
        >
          {openSection === 'debug' ? '▼' : '▶'} Debug Information
        </Button>
        <Button 
          variant="link" 
          onClick={() => toggleSection('json')}
          className="debug-section-button"
        >
          {openSection === 'json' ? '▼' : '▶'} View Component JSON
        </Button>
      </div>
      {openSection === 'debug' && (
        <>
          {metadata && <MetadataViewer metadata={metadata} messageId={messageId} />}
          {(llmInteractions || agentMessages) && (
            <PipelineViewer 
              llmInteractions={llmInteractions} 
              agentMessages={agentMessages}
              messageId={messageId} 
            />
          )}
          {dataTransform && <DataTransformationViewer dataTransform={dataTransform} messageId={messageId} />}
        </>
      )}
      {openSection === 'json' && config && (
        <JsonViewer config={config} messageId={messageId} alwaysExpanded={true} />
      )}
    </div>
  );
}


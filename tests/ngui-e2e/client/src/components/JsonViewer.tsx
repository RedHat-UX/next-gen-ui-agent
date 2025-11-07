import React, { useState } from 'react';
import {
  Button,
  CodeBlock,
  CodeBlockCode,
  Panel,
  PanelMain,
  PanelMainBody,
  Split,
  SplitItem,
  Tooltip
} from '@patternfly/react-core';
import { CopyIcon, CodeIcon, CompressIcon, ExpandIcon } from '@patternfly/react-icons';

interface JsonViewerProps {
  config: any;
  messageId: string;
}

export const JsonViewer: React.FC<JsonViewerProps> = ({ config, messageId }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  
  const jsonString = JSON.stringify(config, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isExpanded) {
    return (
      <div style={{ marginTop: '12px' }}>
        <Button
          variant="link"
          icon={<CodeIcon />}
          onClick={() => setIsExpanded(true)}
          style={{ padding: '4px 8px', fontSize: '13px' }}
        >
          View Component JSON
        </Button>
      </div>
    );
  }

  return (
    <div style={{ marginTop: '12px' }}>
      <Panel variant="bordered" style={{ backgroundColor: 'var(--pf-v6-global--BackgroundColor--light-100)' }}>
        <PanelMain>
          <PanelMainBody>
            <Split hasGutter style={{ marginBottom: '8px', alignItems: 'center' }}>
              <SplitItem isFilled>
                <strong style={{ fontSize: '13px', color: 'var(--pf-v6-global--Color--100)' }}>
                  Component Configuration JSON
                </strong>
              </SplitItem>
              <SplitItem>
                <Tooltip content={copied ? 'Copied!' : 'Copy JSON'}>
                  <Button
                    variant="plain"
                    icon={<CopyIcon />}
                    onClick={handleCopy}
                    aria-label="Copy JSON"
                    style={{ padding: '4px' }}
                  />
                </Tooltip>
              </SplitItem>
              <SplitItem>
                <Tooltip content="Collapse">
                  <Button
                    variant="plain"
                    icon={<CompressIcon />}
                    onClick={() => setIsExpanded(false)}
                    aria-label="Collapse JSON viewer"
                    style={{ padding: '4px' }}
                  />
                </Tooltip>
              </SplitItem>
            </Split>
            
            <CodeBlock
              style={{
                maxHeight: '400px',
                overflow: 'auto'
              }}
            >
              <CodeBlockCode>
                {jsonString}
              </CodeBlockCode>
            </CodeBlock>
            
            <div style={{ 
              marginTop: '8px', 
              fontSize: '12px', 
              color: 'var(--pf-v6-global--Color--200)' 
            }}>
              {Object.keys(config).length} properties • {jsonString.length} characters
            </div>
          </PanelMainBody>
        </PanelMain>
      </Panel>
    </div>
  );
};


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
      <div className="json-viewer-collapsed">
        <Button
          variant="link"
          icon={<CodeIcon />}
          onClick={() => setIsExpanded(true)}
          className="json-viewer-toggle-btn"
        >
          View Component JSON
        </Button>
      </div>
    );
  }

  return (
    <div className="json-viewer-expanded">
      <Panel variant="bordered" className="json-viewer-panel">
        <PanelMain>
          <PanelMainBody>
            <Split hasGutter className="json-viewer-header">
              <SplitItem isFilled>
                <strong className="json-viewer-title">
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
                    className="json-viewer-icon-btn"
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
                    className="json-viewer-icon-btn"
                  />
                </Tooltip>
              </SplitItem>
            </Split>
            
            <CodeBlock className="json-viewer-code">
              <CodeBlockCode>
                {jsonString}
              </CodeBlockCode>
            </CodeBlock>
            
            <div className="json-viewer-stats">
              {Object.keys(config).length} properties • {jsonString.length} characters
            </div>
          </PanelMainBody>
        </PanelMain>
      </Panel>
    </div>
  );
};


import React, { useState } from 'react';
import {
  Card,
  CardBody,
  Title,
  ExpandableSection,
  Stack,
  StackItem,
  Label
} from '@patternfly/react-core';

interface AgentMessage {
  type: string;
  content: string;
  tool_calls?: { name: string; args: any }[];
  name?: string;
}

interface AgentMessagesViewerProps {
  messages?: AgentMessage[];
  messageId: string;
}

export const AgentMessagesViewer: React.FC<AgentMessagesViewerProps> = ({ messages, messageId }) => {
  const [expandedMessages, setExpandedMessages] = useState<Set<number>>(new Set());

  if (!messages || messages.length === 0) {
    return null;
  }

  const toggleMessage = (index: number) => {
    setExpandedMessages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const getMessageTypeColor = (type: string): 'blue' | 'green' | 'orange' | 'purple' | 'grey' => {
    switch (type) {
      case 'HumanMessage':
        return 'blue';
      case 'AIMessage':
        return 'green';
      case 'ToolMessage':
        return 'orange';
      default:
        return 'grey';
    }
  };

  return (
    <Card isCompact className="agent-messages-viewer" style={{ marginBottom: '1rem', overflow: 'visible' }}>
      <CardBody style={{ overflow: 'visible' }}>
        <Title headingLevel="h6" size="md" style={{ marginBottom: '0.5rem' }}>
          🔍 Agent Execution Trace
        </Title>
        <Stack hasGutter>
          {messages.map((msg, index) => (
            <StackItem key={`${messageId}-msg-${index}`}>
              <ExpandableSection
                toggleText={
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Label color={getMessageTypeColor(msg.type)}>{msg.type}</Label>
                    {msg.tool_calls && msg.tool_calls.length > 0 && (
                      <Label color="purple">
                        {msg.tool_calls.length} tool call{msg.tool_calls.length > 1 ? 's' : ''}
                      </Label>
                    )}
                    {msg.name && <Label color="cyan">{msg.name}</Label>}
                  </div>
                }
                isExpanded={expandedMessages.has(index)}
                onToggle={() => toggleMessage(index)}
              >
                <div style={{ paddingLeft: '1rem', paddingTop: '0.5rem' }}>
                  {/* Content */}
                  {msg.content && (
                    <div style={{ marginBottom: '0.75rem' }}>
                      <strong style={{ fontSize: '0.875rem', color: '#6a6e73' }}>Content:</strong>
                      <pre style={{ 
                        fontSize: '0.75rem',
                        backgroundColor: '#f5f5f5',
                        padding: '0.5rem',
                        borderRadius: '4px',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        margin: '0.5rem 0 0 0',
                        overflow: 'visible'
                      }}>
                        <code>{msg.content}</code>
                      </pre>
                    </div>
                  )}

                  {/* Tool Calls */}
                  {msg.tool_calls && msg.tool_calls.length > 0 && (
                    <div>
                      <strong style={{ fontSize: '0.875rem', color: '#6a6e73' }}>Tool Calls:</strong>
                      {msg.tool_calls.map((tc, tcIndex) => (
                        <div key={tcIndex} style={{ 
                          marginTop: '0.5rem', 
                          padding: '0.5rem', 
                          backgroundColor: '#f5f5f5',
                          borderRadius: '4px',
                          fontSize: '0.75rem'
                        }}>
                          <div><strong>Tool:</strong> {tc.name}</div>
                          {Object.keys(tc.args).length > 0 && (
                            <div style={{ marginTop: '0.25rem' }}>
                              <strong>Args:</strong> {JSON.stringify(tc.args)}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </ExpandableSection>
            </StackItem>
          ))}
        </Stack>
      </CardBody>
    </Card>
  );
};


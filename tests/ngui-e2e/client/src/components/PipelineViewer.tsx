import React from 'react';
import {
  Card,
  CardBody,
  CardTitle,
  ExpandableSection,
} from '@patternfly/react-core';

interface PipelineViewerProps {
  agentMessages?: Array<{
    type: string;
    content: string;
    tool_calls?: Array<{ name: string; args: Record<string, unknown> }>;
    name?: string;
  }>;
  llmInteractions?: Array<{
    step: string;
    system_prompt: string;
    user_prompt: string;
    raw_response: string;
  }>;
  messageId: string;
}

export function PipelineViewer({
  agentMessages,
  llmInteractions,
  messageId,
}: PipelineViewerProps) {
  const [expandedMovies, setExpandedMovies] = React.useState(false);
  const [expandedNgui, setExpandedNgui] = React.useState(false);

  if (!agentMessages && !llmInteractions) {
    return null;
  }

  return (
    <Card className="pipeline-viewer-card">
      <CardTitle className="pipeline-viewer-title">
        <div className="pipeline-viewer-title-wrapper">
          <span className="pipeline-viewer-emoji">🔍</span>
          <strong>Debug Pipeline</strong>
        </div>
      </CardTitle>
      <CardBody className="pipeline-viewer-body">
        {/* Movies Agent Stage */}
        {agentMessages && agentMessages.length > 0 && (
        <Card className="pipeline-stage-card-movies">
          <CardTitle className="pipeline-stage-title">
            <div className="pipeline-viewer-title-wrapper">
              <span className="pipeline-viewer-emoji">🎬</span>
              <strong>Stage 1: Movies Agent</strong>
              <span className="pipeline-stage-description">
                (Agentic LLM fetching data from database)
              </span>
            </div>
          </CardTitle>
          <CardBody className="pipeline-stage-body">
            <ExpandableSection
              toggleText={`View ${agentMessages.length} message(s)`}
              onToggle={(_event, isExpanded) => setExpandedMovies(isExpanded)}
              isExpanded={expandedMovies}
            >
              {agentMessages.map((msg, idx) => (
                <div 
                  key={`${messageId}-movies-${idx}`}
                  className="pipeline-message-item"
                  style={{ marginBottom: idx < agentMessages.length - 1 ? '8px' : '0' }}
                >
                  <div className={`pipeline-message-type-badge ${
                    msg.type === 'HumanMessage' ? 'pipeline-message-type-human' : 
                    msg.type === 'AIMessage' ? 'pipeline-message-type-ai' :
                    'pipeline-message-type-tool'
                  }`}>
                    {msg.type}
                  </div>
                  
                  {msg.tool_calls && msg.tool_calls.length > 0 && (
                    <div className="pipeline-tool-calls-section">
                      <strong className="pipeline-tool-calls-title">Tool Calls:</strong>
                      {msg.tool_calls.map((tc, tcIdx) => (
                        <div key={tcIdx} className="pipeline-tool-call-item">
                          <code className="pipeline-tool-call-name">
                            {tc.name}
                          </code>
                          <pre className="pipeline-tool-call-args">
                            {JSON.stringify(tc.args, null, 2)}
                          </pre>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {msg.name && (
                    <div className="pipeline-tool-name-section">
                      <strong className="pipeline-tool-name-title">Tool:</strong>{' '}
                      <code className="pipeline-tool-name-code">
                        {msg.name}
                      </code>
                    </div>
                  )}
                  
                  <div>
                    <strong className="pipeline-content-title">Content:</strong>
                    <pre className="pipeline-content-pre">
{msg.content}
                    </pre>
                  </div>
                </div>
              ))}
            </ExpandableSection>
          </CardBody>
        </Card>
        )}

        {/* NGUI Agent Stage */}
        {llmInteractions && llmInteractions.length > 0 && (
        <Card className="pipeline-stage-card-ngui">
          <CardTitle className="pipeline-stage-title">
            <div className="pipeline-viewer-title-wrapper">
              <span className="pipeline-viewer-emoji">🎨</span>
              <strong>Stage 2: NGUI Agent</strong>
              <span className="pipeline-stage-description">
                (LLM selecting and configuring UI component)
              </span>
            </div>
          </CardTitle>
          <CardBody className="pipeline-stage-body">
            <ExpandableSection
              toggleText={`${llmInteractions[0]?.step || 'Component Selection'}`}
              onToggle={(_event, isExpanded) => setExpandedNgui(isExpanded)}
              isExpanded={expandedNgui}
            >
              {llmInteractions.map((interaction, idx) => (
                <div 
                  key={`${messageId}-ngui-${idx}`}
                  className="pipeline-interaction-item"
                  style={{ marginBottom: idx < llmInteractions.length - 1 ? '8px' : '0' }}
                >
                  <div className="pipeline-interaction-section">
                    <strong className="pipeline-interaction-title">System Prompt:</strong>
                    <pre className="pipeline-interaction-pre-system">
{interaction.system_prompt}
                    </pre>
                  </div>
                  <div className="pipeline-interaction-section">
                    <strong className="pipeline-interaction-title">User Prompt:</strong>
                    <pre className="pipeline-interaction-pre-user">
{interaction.user_prompt}
                    </pre>
                  </div>
                  <div className="pipeline-interaction-section">
                    <strong className="pipeline-interaction-title">LLM Response:</strong>
                    <pre className="pipeline-interaction-pre-response">
{interaction.raw_response}
                    </pre>
                  </div>
                </div>
              ))}
            </ExpandableSection>
          </CardBody>
        </Card>
        )}
      </CardBody>
    </Card>
  );
}

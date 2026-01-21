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
  inputDataType?: string;
  configMappings?: Record<string, string>;
  messageId: string;
}

export function PipelineViewer({
  agentMessages,
  llmInteractions,
  inputDataType,
  configMappings,
  messageId,
}: PipelineViewerProps) {
  const [expandedDataAgent, setExpandedDataAgent] = React.useState(false);
  const [expandedNgui, setExpandedNgui] = React.useState(false);

  if (!agentMessages && !llmInteractions) {
    return null;
  }

  // Detect agent type from tool calls
  const detectAgentType = () => {
    if (!agentMessages || agentMessages.length === 0) {
      return { name: 'Data Agent', emoji: '🔧', description: '(Agentic LLM fetching data)' };
    }
    
    // Check for OpenShift tools
    const hasOpenShiftTools = agentMessages.some(msg => 
      msg.tool_calls?.some(tc => 
        tc.name?.startsWith('get_openshift_')
      ) || msg.name?.startsWith('get_openshift_')
    );
    
    if (hasOpenShiftTools) {
      return { name: 'OpenShift Agent', emoji: '☸️', description: '(Agentic LLM fetching OpenShift cluster data)' };
    }
    
    // Check for movie tools
    const hasMovieTools = agentMessages.some(msg => 
      msg.tool_calls?.some(tc => 
        tc.name === 'search_movie' || tc.name === 'get_all_movies'
      ) || msg.name === 'search_movie' || msg.name === 'get_all_movies'
    );
    
    if (hasMovieTools) {
      return { name: 'Movies Agent', emoji: '🎬', description: '(Agentic LLM fetching data from database)' };
    }
    
    // Default
    return { name: 'Data Agent', emoji: '🔧', description: '(Agentic LLM fetching data)' };
  };

  const agentInfo = detectAgentType();

  // Extract tool names from agent messages
  const toolNames = new Set<string>();
  agentMessages?.forEach(msg => {
    if (msg.tool_calls) {
      msg.tool_calls.forEach(tc => {
        if (tc.name) toolNames.add(tc.name);
      });
    }
    if (msg.name) toolNames.add(msg.name);
  });

  return (
    <Card className="pipeline-viewer-card">
      <CardTitle className="pipeline-viewer-title">
        <div className="pipeline-viewer-title-wrapper">
          <span className="pipeline-viewer-emoji">🔍</span>
          <strong>Debug Pipeline</strong>
        </div>
      </CardTitle>
      <CardBody className="pipeline-viewer-body">
        {/* Tool Name → InputData.type Mapping (for OpenShift/MCP queries) */}
        {toolNames.size > 0 && inputDataType && (
          <Card className="pipeline-stage-card-movies" style={{ marginBottom: '16px', backgroundColor: '#f0f0f0' }}>
            <CardTitle className="pipeline-stage-title">
              <div className="pipeline-viewer-title-wrapper">
                <span className="pipeline-viewer-emoji">🔗</span>
                <strong>Automatic Mapping</strong>
                <span className="pipeline-stage-description">
                  (Tool name → InputData.type)
                </span>
              </div>
            </CardTitle>
            <CardBody className="pipeline-stage-body">
              <div style={{ padding: '8px 0' }}>
                <div style={{ marginBottom: '8px' }}>
                  <strong>Tool Name(s):</strong>{' '}
                  <code style={{ backgroundColor: '#e8e8e8', padding: '2px 6px', borderRadius: '3px' }}>
                    {Array.from(toolNames).join(', ')}
                  </code>
                </div>
                <div>
                  <strong>→ InputData.type:</strong>{' '}
                  <code style={{ backgroundColor: '#e8e8e8', padding: '2px 6px', borderRadius: '3px', fontWeight: 'bold' }}>
                    {inputDataType}
                  </code>
                </div>
                {configMappings && Object.keys(configMappings).length > 0 && (
                  <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #ddd' }}>
                    <strong style={{ fontSize: '0.9em' }}>Formatter Config Applied:</strong>
                    <div style={{ marginTop: '4px', fontSize: '0.85em' }}>
                      {Object.entries(configMappings).map(([key, value]) => (
                        <div key={key} style={{ marginTop: '4px' }}>
                          <code style={{ backgroundColor: '#e8e8e8', padding: '2px 6px', borderRadius: '3px' }}>
                            {key}
                          </code>
                          {' → '}
                          <code style={{ backgroundColor: '#e8e8e8', padding: '2px 6px', borderRadius: '3px' }}>
                            {value}
                          </code>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                <div style={{ marginTop: '12px', fontSize: '0.9em', color: '#666', fontStyle: 'italic' }}>
                  The <code>data_selection</code> node automatically maps <code>ToolMessage.name</code> to <code>InputData.type</code>,
                  which determines which formatter configuration is applied.
                </div>
              </div>
            </CardBody>
          </Card>
        )}
        {/* Data Agent Stage (Movies, OpenShift, or generic) */}
        {agentMessages && agentMessages.length > 0 && (
        <Card className="pipeline-stage-card-movies">
          <CardTitle className="pipeline-stage-title">
            <div className="pipeline-viewer-title-wrapper">
              <span className="pipeline-viewer-emoji">{agentInfo.emoji}</span>
              <strong>Stage 1: {agentInfo.name}</strong>
              <span className="pipeline-stage-description">
                {agentInfo.description}
              </span>
            </div>
          </CardTitle>
          <CardBody className="pipeline-stage-body">
            <ExpandableSection
              toggleText={`View ${agentMessages.length} message(s)`}
              onToggle={(_event, isExpanded) => setExpandedDataAgent(isExpanded)}
              isExpanded={expandedDataAgent}
            >
              {agentMessages.map((msg, idx) => (
                <div 
                  key={`${messageId}-data-agent-${idx}`}
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

import React, { useState } from 'react';
import {
  Panel,
  PanelMain,
  PanelMainBody,
  Tabs,
  Tab,
  TabTitleText,
  Badge,
  FormGroup,
  Radio
} from '@patternfly/react-core';
import { MockModeToggle } from './MockModeToggle';
import { QuickPrompts } from './QuickPrompts';
import { PrometheusConverter } from './PrometheusConverter';

interface ModelInfo {
  name: string;
  baseUrl: string;
}

interface TestPanelProps {
  // Mock Mode props
  isMockMode: boolean;
  onMockModeChange: (enabled: boolean) => void;
  selectedMock?: string;
  onMockSelect: (mockName: string) => void;
  customJson?: string;
  onCustomJsonChange: (json: string) => void;
  onSendCustomJson: () => void;
  onSendMockDirect: (config: any, label: string) => void;
  
  // Quick Prompts props
  onPromptSelect: (prompt: string) => void;
  disabled?: boolean;
  
  // Model Info
  modelInfo?: ModelInfo;
  selectedStrategy: 'one-step' | 'two-step';
  onStrategyChange: (strategy: 'one-step' | 'two-step') => void;
}

export const TestPanel: React.FC<TestPanelProps> = ({
  isMockMode,
  onMockModeChange,
  selectedMock,
  onMockSelect,
  customJson,
  onCustomJsonChange,
  onSendCustomJson,
  onSendMockDirect,
  onPromptSelect,
  disabled = false,
  modelInfo,
  selectedStrategy,
  onStrategyChange
}) => {
  const [activeTabKey, setActiveTabKey] = useState<string | number>(0);

  const handleTabClick = (
    _event: React.MouseEvent<HTMLElement, MouseEvent>,
    tabIndex: string | number
  ) => {
    setActiveTabKey(tabIndex);
  };

  return (
    <div className="test-panel-container">
      <div className="test-panel-header">
        <h2 className="test-panel-title">
          🧪 Test & Debug Panel
        </h2>
        <p className="test-panel-subtitle">
          Test components with live agent or mock data
        </p>
      </div>
      
      <Panel variant="bordered" className="test-panel-flex">
        <PanelMain className="test-panel-flex">
          <PanelMainBody className="test-panel-body">
            <Tabs 
              activeKey={activeTabKey} 
              onSelect={handleTabClick}
              aria-label="Test and debug options"
            >
            <Tab 
              eventKey={0} 
              title={
                <TabTitleText>
                  🚀 Quick Prompts {!isMockMode && <Badge isRead>Live</Badge>}
                </TabTitleText>
              }
              aria-label="Quick test prompts"
            >
              <div className="test-panel-tab-content">
                {isMockMode ? (
                  <div className="test-panel-disabled-message">
                    <p><strong>Quick Prompts are disabled in Mock Mode</strong></p>
                    <p className="test-panel-disabled-hint">
                      Switch to the Mock Mode tab and turn off Mock Mode to use Quick Prompts with the live agent.
                    </p>
                  </div>
                ) : (
                  <QuickPrompts 
                    onPromptSelect={onPromptSelect}
                    disabled={disabled}
                  />
                )}
              </div>
            </Tab>

            <Tab 
              eventKey={1} 
              title={
                <TabTitleText>
                  🎭 Mock Mode {isMockMode && <Badge>Active</Badge>}
                </TabTitleText>
              }
              aria-label="Mock mode configuration"
            >
              <div className="test-panel-tab-content">
                <MockModeToggle
                  isMockMode={isMockMode}
                  onMockModeChange={onMockModeChange}
                  selectedMock={selectedMock}
                  onMockSelect={onMockSelect}
                  customJson={customJson}
                  onCustomJsonChange={onCustomJsonChange}
                  onSendCustomJson={onSendCustomJson}
                  onSendMockDirect={onSendMockDirect}
                />
              </div>
            </Tab>

            <Tab 
              eventKey={2} 
              title={
                <TabTitleText>
                  🤖 Model Info
                </TabTitleText>
              }
              aria-label="Model information"
            >
              <div className="test-panel-tab-content">
                {modelInfo ? (
                  <div className="test-panel-model-info">
                    <h3 className="test-panel-section-title">
                      Connected LLM
                    </h3>
                    <div className="test-panel-info-list">
                      <div>
                        <strong className="test-panel-info-label">Model Name:</strong>
                        <div className="test-panel-info-value">
                          {modelInfo.name}
                        </div>
                      </div>
                      <div>
                        <strong className="test-panel-info-label">Base URL:</strong>
                        <div className="test-panel-info-value">
                          {modelInfo.baseUrl}
                        </div>
                      </div>
                    </div>
                    
                    <div className="test-panel-strategy-section">
                      <h3 className="test-panel-section-title">
                        Component Selection Strategy
                      </h3>
                      <FormGroup role="radiogroup">
                        <Radio
                          name="strategy"
                          id="strategy-one-step"
                          label="One-step (faster, single LLM call)"
                          isChecked={selectedStrategy === 'one-step'}
                          onChange={() => onStrategyChange('one-step')}
                        />
                        <Radio
                          name="strategy"
                          id="strategy-two-step"
                          label="Two-step (more deliberate, two LLM calls)"
                          isChecked={selectedStrategy === 'two-step'}
                          onChange={() => onStrategyChange('two-step')}
                        />
                      </FormGroup>
                      <div className="test-panel-strategy-current">
                        <strong>Current:</strong> {selectedStrategy}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="test-panel-model-info-unavailable">
                    <p>Model information not available</p>
                  </div>
                )}
              </div>
            </Tab>

            <Tab 
              eventKey={3} 
              title={
                <TabTitleText>
                  📊 Prometheus
                </TabTitleText>
              }
              aria-label="Prometheus data converter"
            >
              <div className="test-panel-tab-content">
                <PrometheusConverter
                  onConvert={(config) => onSendMockDirect(config, 'Prometheus Chart')}
                />
              </div>
            </Tab>
            </Tabs>
          </PanelMainBody>
        </PanelMain>
      </Panel>
    </div>
  );
};


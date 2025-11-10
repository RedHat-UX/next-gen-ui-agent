import React, { useState } from 'react';
import {
  Panel,
  PanelMain,
  PanelMainBody,
  Tabs,
  Tab,
  TabTitleText,
  Badge
} from '@patternfly/react-core';
import { MockModeToggle } from './MockModeToggle';
import { QuickPrompts } from './QuickPrompts';

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
  disabled = false
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
              title={<TabTitleText>ℹ️ Help</TabTitleText>}
              aria-label="Help and information"
            >
              <div className="test-panel-tab-content">
                <div className="help-content">
                  <h3 className="help-section-title">🚀 Quick Prompts</h3>
                  <p className="help-text">
                    One-click test prompts that go through the <strong>real LLM pipeline</strong>.
                    Perfect for integration testing and verifying agent behavior.
                  </p>
                  <ul className="help-list">
                    <li>17 pre-configured prompts</li>
                    <li>Tests: Cards, Tables, Charts, Media, Mixed components</li>
                    <li>Full backend processing with real agent</li>
                    <li>Expected component type shown on each card</li>
                  </ul>

                  <h3 className="help-section-title help-section-title-spacing">🎭 Mock Mode</h3>
                  <p className="help-text">
                    Test UI rendering <strong>without calling the backend</strong>.
                    Perfect for rapid UI development and component testing.
                  </p>
                  <ul className="help-list">
                    <li>8 pre-configured component examples</li>
                    <li>Instant rendering (no agent delay)</li>
                    <li>Preview & edit JSON before sending</li>
                    <li>Custom JSON input for testing</li>
                  </ul>

                  <h3 className="help-section-title help-section-title-spacing">📊 Comparison</h3>
                  <div className="help-comparison-grid">
                    <div className="help-comparison-card">
                      <strong>Quick Prompts</strong>
                      <ul className="help-comparison-list">
                        <li>Full pipeline test</li>
                        <li>Real agent (2-5 sec)</li>
                        <li>Integration testing</li>
                        <li>Live backend required</li>
                      </ul>
                    </div>
                    <div className="help-comparison-card">
                      <strong>Mock Mode</strong>
                      <ul className="help-comparison-list">
                        <li>UI testing only</li>
                        <li>Instant rendering</li>
                        <li>Component development</li>
                        <li>No backend needed</li>
                      </ul>
                    </div>
                  </div>

                  <h3 className="help-section-title help-section-title-spacing">💡 Tips</h3>
                  <ul className="help-list">
                    <li><strong>Start with Mock Mode</strong> - Perfect your component UI</li>
                    <li><strong>Switch to Quick Prompts</strong> - Verify real agent behavior</li>
                    <li><strong>Iterate</strong> - Toggle between both as needed</li>
                    <li><strong>Check Expected vs Actual</strong> - Each prompt shows expected component type</li>
                  </ul>

                  <div className="help-doc-box">
                    <strong>📚 Documentation:</strong>
                    <ul className="help-doc-list">
                      <li>QUICK_PROMPTS_GUIDE.md</li>
                      <li>MOCK_MODE_GUIDE.md</li>
                      <li>EXTENDED_MOCK_GUIDE.md</li>
                      <li>MOCKABLE_PIPELINE_ANALYSIS.md</li>
                    </ul>
                  </div>
                </div>
              </div>
            </Tab>
            </Tabs>
          </PanelMainBody>
        </PanelMain>
      </Panel>
    </div>
  );
};


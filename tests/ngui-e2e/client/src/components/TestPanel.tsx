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
            </Tabs>
          </PanelMainBody>
        </PanelMain>
      </Panel>
    </div>
  );
};


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
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ 
        marginBottom: '16px',
        paddingBottom: '12px',
        borderBottom: '1px solid var(--pf-v6-global--BorderColor--100)'
      }}>
        <h2 style={{ 
          margin: 0, 
          fontSize: '20px',
          fontWeight: 600,
          color: 'var(--pf-v6-global--Color--100)'
        }}>
          🧪 Test & Debug Panel
        </h2>
        <p style={{ 
          margin: '4px 0 0 0',
          fontSize: '13px',
          color: 'var(--pf-v6-global--Color--200)'
        }}>
          Test components with live agent or mock data
        </p>
      </div>
      
      <Panel variant="bordered" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <PanelMain style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <PanelMainBody style={{ flex: 1, overflow: 'auto' }}>
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
              <div style={{ paddingTop: '16px' }}>
                {isMockMode ? (
                  <div style={{ textAlign: 'center', padding: '20px', color: 'var(--pf-v6-global--Color--200)' }}>
                    <p><strong>Quick Prompts are disabled in Mock Mode</strong></p>
                    <p style={{ fontSize: '14px', marginTop: '8px' }}>
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
              <div style={{ paddingTop: '16px' }}>
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
              <div style={{ paddingTop: '16px' }}>
                <div style={{ padding: '0 16px' }}>
                  <h3 style={{ marginTop: 0 }}>🚀 Quick Prompts</h3>
                  <p style={{ color: 'var(--pf-v6-global--Color--200)' }}>
                    One-click test prompts that go through the <strong>real LLM pipeline</strong>.
                    Perfect for integration testing and verifying agent behavior.
                  </p>
                  <ul style={{ marginLeft: '20px', color: 'var(--pf-v6-global--Color--200)' }}>
                    <li>17 pre-configured prompts</li>
                    <li>Tests: Cards, Tables, Charts, Media, Mixed components</li>
                    <li>Full backend processing with real agent</li>
                    <li>Expected component type shown on each card</li>
                  </ul>

                  <h3 style={{ marginTop: '24px' }}>🎭 Mock Mode</h3>
                  <p style={{ color: 'var(--pf-v6-global--Color--200)' }}>
                    Test UI rendering <strong>without calling the backend</strong>.
                    Perfect for rapid UI development and component testing.
                  </p>
                  <ul style={{ marginLeft: '20px', color: 'var(--pf-v6-global--Color--200)' }}>
                    <li>8 pre-configured component examples</li>
                    <li>Instant rendering (no agent delay)</li>
                    <li>Preview & edit JSON before sending</li>
                    <li>Custom JSON input for testing</li>
                  </ul>

                  <h3 style={{ marginTop: '24px' }}>📊 Comparison</h3>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr 1fr', 
                    gap: '16px',
                    marginTop: '12px'
                  }}>
                    <div style={{ 
                      padding: '12px', 
                      border: '1px solid var(--pf-v6-global--BorderColor--100)',
                      borderRadius: '4px'
                    }}>
                      <strong>Quick Prompts</strong>
                      <ul style={{ 
                        marginLeft: '20px', 
                        fontSize: '13px',
                        color: 'var(--pf-v6-global--Color--200)',
                        marginTop: '8px'
                      }}>
                        <li>Full pipeline test</li>
                        <li>Real agent (2-5 sec)</li>
                        <li>Integration testing</li>
                        <li>Live backend required</li>
                      </ul>
                    </div>
                    <div style={{ 
                      padding: '12px', 
                      border: '1px solid var(--pf-v6-global--BorderColor--100)',
                      borderRadius: '4px'
                    }}>
                      <strong>Mock Mode</strong>
                      <ul style={{ 
                        marginLeft: '20px', 
                        fontSize: '13px',
                        color: 'var(--pf-v6-global--Color--200)',
                        marginTop: '8px'
                      }}>
                        <li>UI testing only</li>
                        <li>Instant rendering</li>
                        <li>Component development</li>
                        <li>No backend needed</li>
                      </ul>
                    </div>
                  </div>

                  <h3 style={{ marginTop: '24px' }}>💡 Tips</h3>
                  <ul style={{ marginLeft: '20px', color: 'var(--pf-v6-global--Color--200)' }}>
                    <li><strong>Start with Mock Mode</strong> - Perfect your component UI</li>
                    <li><strong>Switch to Quick Prompts</strong> - Verify real agent behavior</li>
                    <li><strong>Iterate</strong> - Toggle between both as needed</li>
                    <li><strong>Check Expected vs Actual</strong> - Each prompt shows expected component type</li>
                  </ul>

                  <div style={{ 
                    marginTop: '24px', 
                    padding: '12px', 
                    backgroundColor: 'var(--pf-v6-global--BackgroundColor--light-100)',
                    borderRadius: '4px',
                    fontSize: '13px'
                  }}>
                    <strong>📚 Documentation:</strong>
                    <ul style={{ marginLeft: '20px', marginTop: '8px', marginBottom: 0 }}>
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


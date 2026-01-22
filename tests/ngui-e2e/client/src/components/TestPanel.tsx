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
  Radio,
  TextArea,
  TextInput,
  FormSelect,
  FormSelectOption,
  Button
} from '@patternfly/react-core';
import { AngleLeftIcon, AngleRightIcon } from '@patternfly/react-icons';
import { MockModeToggle } from './MockModeToggle';
import { QuickPrompts } from './QuickPrompts';
import { INLINE_DATASETS } from '../data/inlineDatasets';
import type { QuickPrompt } from '../quickPrompts';

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
  onPromptSelect: (prompt: QuickPrompt) => void;
  disabled?: boolean;
  
  // Model Info
  modelInfo?: ModelInfo;
  selectedStrategy: 'one-step' | 'two-step';
  onStrategyChange: (strategy: 'one-step' | 'two-step') => void;
  inlineDataset: string;
  onInlineDatasetChange: (value: string) => void;
  inlineDatasetType: string;
  onInlineDatasetTypeChange: (value: string) => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
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
  onStrategyChange,
  inlineDataset,
  onInlineDatasetChange,
  inlineDatasetType,
  onInlineDatasetTypeChange,
  isCollapsed = false,
  onToggleCollapse,
}) => {
  const [activeTabKey, setActiveTabKey] = useState<string | number>(0);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');

  const handleDatasetChange = (value: string) => {
    setSelectedDatasetId(value);
    if (!value) {
      onInlineDatasetChange('');
      onInlineDatasetTypeChange('');
      return;
    }
    const dataset = INLINE_DATASETS.find((d) => d.id === value);
    if (dataset) {
      onInlineDatasetChange(JSON.stringify(dataset.payload, null, 2));
      onInlineDatasetTypeChange(dataset.dataType ?? '');
    }
  };

  const handleTabClick = (
    _event: React.MouseEvent<HTMLElement, MouseEvent>,
    tabIndex: string | number
  ) => {
    setActiveTabKey(tabIndex);
  };

  return (
    <div className={`test-panel-container ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="test-panel-header">
        {!isCollapsed && (
          <>
            <h2 className="test-panel-title">
              🧪 Test & Debug Panel
            </h2>
          </>
        )}
        {onToggleCollapse && (
          <Button
            variant="plain"
            onClick={onToggleCollapse}
            aria-label={isCollapsed ? 'Expand panel' : 'Collapse panel'}
            className="test-panel-collapse-button"
          >
            {isCollapsed ? <AngleRightIcon /> : <AngleLeftIcon />}
          </Button>
        )}
      </div>
      
      {!isCollapsed && (
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
                  🗂️ Inline Dataset
                </TabTitleText>
              }
              aria-label="Inline dataset attachment"
            >
              <div className="test-panel-tab-content inline-dataset-tab">
                <p className="test-panel-inline-description">
                  Attach custom JSON data to your next live request. When populated, the backend skips the movies agent and feeds this dataset directly to the renderer.
                </p>

                {/* Predefined Datasets Section */}
                <div className="inline-dataset-section">
                  <div className="inline-dataset-group">
                    <h4 className="inline-dataset-group-title">
                      <span className="inline-dataset-group-icon">📦</span>
                      Load Predefined Dataset
                    </h4>
                    <FormGroup label="Select dataset" fieldId="inline-dataset-select">
                      <FormSelect
                        id="inline-dataset-select"
                        value={selectedDatasetId}
                        onChange={(_event, value) => handleDatasetChange(value)}
                      >
                        <FormSelectOption key="none" value="" label="None (manual input)" />
                        {INLINE_DATASETS.map((dataset) => (
                          <FormSelectOption
                            key={dataset.id}
                            value={dataset.id}
                            label={dataset.label}
                          />
                        ))}
                      </FormSelect>
                      {selectedDatasetId && (
                        <p className="test-panel-inline-description small">
                          {INLINE_DATASETS.find((d) => d.id === selectedDatasetId)?.description}
                        </p>
                      )}
                    </FormGroup>
                  </div>
                </div>

                {/* Custom Dataset Section */}
                <div className="inline-dataset-section">
                  <div className="inline-dataset-group">
                    <h4 className="inline-dataset-group-title">
                      <span className="inline-dataset-group-icon">✏️</span>
                      Custom Dataset
                    </h4>
                    
                    <FormGroup label="Dataset type (optional)" fieldId="inline-dataset-type">
                      <TextInput
                        id="inline-dataset-type"
                        value={inlineDatasetType}
                        onChange={(_, value) => onInlineDatasetTypeChange(value)}
                        placeholder="e.g. lightrail.costs, infra.metrics"
                      />
                      <p className="inline-dataset-help-text">
                        Identifier for data transformer selection (e.g., "movies.detail", "cost.analysis")
                      </p>
                    </FormGroup>
                    
                    <FormGroup label="Dataset JSON" fieldId="inline-dataset-json">
                      <TextArea
                        id="inline-dataset-json"
                        value={inlineDataset}
                        onChange={(_, value) => onInlineDatasetChange(value)}
                        placeholder='[{ "name": "Service A", "value": 42 }]'
                        rows={10}
                      />
                      <p className="inline-dataset-help-text">
                        Paste JSON array or object. Supports standard JSON and other formats.
                      </p>
                    </FormGroup>
                  </div>
                </div>

                {/* Hint Box */}
                <div className="test-panel-inline-hint">
                  <p>
                    💡 <strong>Tip:</strong> Leave blank to use the standard movies dataset, or paste custom JSON to test with your own data.
                  </p>
                </div>
              </div>
            </Tab>
            </Tabs>
          </PanelMainBody>
        </PanelMain>
      </Panel>
      )}
    </div>
  );
};


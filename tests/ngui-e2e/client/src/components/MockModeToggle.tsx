import React from 'react';
import {
  Switch,
  Select,
  SelectOption,
  SelectList,
  MenuToggle,
  TextArea,
  Button,
  Stack,
  StackItem,
  Alert
} from '@patternfly/react-core';
import { mockComponentData } from '../mockData';
import type { MockDataItem } from '../mockData';

interface MockModeToggleProps {
  isMockMode: boolean;
  onMockModeChange: (enabled: boolean) => void;
  selectedMock?: string;
  onMockSelect: (mockName: string) => void;
  customJson?: string;
  onCustomJsonChange: (json: string) => void;
  onSendCustomJson: () => void;
  onSendMockDirect: (config: any, label: string) => void;
}

export const MockModeToggle: React.FC<MockModeToggleProps> = ({
  isMockMode,
  onMockModeChange,
  selectedMock,
  onMockSelect,
  customJson = '',
  onCustomJsonChange,
  onSendCustomJson,
  onSendMockDirect
}) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [showCustomJson, setShowCustomJson] = React.useState(false);
  const [jsonError, setJsonError] = React.useState<string>('');
  const [previewJson, setPreviewJson] = React.useState<string>('');
  const [isEditing, setIsEditing] = React.useState(false);
  const [currentMockName, setCurrentMockName] = React.useState<string>('');

  const onToggleClick = () => {
    setIsOpen(!isOpen);
  };

  const onSelect = (_event: React.MouseEvent<Element, MouseEvent> | undefined, value: string | number | undefined) => {
    if (typeof value === 'string') {
      setIsOpen(false);
      // Store the selected mock name locally for the label
      setCurrentMockName(value);
      // Get the config and show it as formatted JSON
      const item = mockComponentData.find(item => item.name === value);
      if (item) {
        setPreviewJson(JSON.stringify(item.config, null, 2));
        setIsEditing(true);
        setJsonError('');
      }
    }
  };

  const validateAndSendPreviewJson = () => {
    try {
      const config = JSON.parse(previewJson); // Validate and parse JSON
      setJsonError('');
      // Use the direct send method with the same label as the selected item
      const label = currentMockName || 'Modified Mock';
      onSendMockDirect(config, label);
      setIsEditing(false);
      setPreviewJson('');
      setCurrentMockName('');
    } catch (e) {
      setJsonError(`Invalid JSON: ${(e as Error).message}`);
    }
  };

  const handleSendOriginal = () => {
    if (currentMockName) {
      onMockSelect(currentMockName);
    }
    setIsEditing(false);
    setPreviewJson('');
    setCurrentMockName('');
  };

  const validateAndSendJson = () => {
    try {
      JSON.parse(customJson);
      setJsonError('');
      onSendCustomJson();
    } catch (e) {
      setJsonError(`Invalid JSON: ${(e as Error).message}`);
    }
  };

  return (
    <Stack hasGutter>
            <StackItem>
              <Switch
                id="mock-mode-switch"
                label={isMockMode ? "Mock Mode (Test UI without Agent)" : "Live Agent Mode"}
                isChecked={isMockMode}
                onChange={(_event, checked) => onMockModeChange(checked)}
              />
            </StackItem>

            {isMockMode && (
              <>
                <StackItem>
                  <Select
                    id="mock-select"
                    isOpen={isOpen}
                    selected={currentMockName || selectedMock}
                    onSelect={onSelect}
                    onOpenChange={(isOpen) => setIsOpen(isOpen)}
                    maxMenuHeight="400px"
                    toggle={(toggleRef: React.Ref<any>) => (
                      <MenuToggle
                        ref={toggleRef}
                        onClick={onToggleClick}
                        isExpanded={isOpen}
                        className="mock-toggle-menu"
                      >
                        {currentMockName || selectedMock || 'Select a mock component...'}
                      </MenuToggle>
                    )}
                  >
                    <SelectList>
                      {mockComponentData.map((item: MockDataItem, index: number) => (
                        <SelectOption key={index} value={item.name}>
                          <strong>{item.name}</strong>
                          <br />
                          <small>{item.description}</small>
                        </SelectOption>
                      ))}
                    </SelectList>
                  </Select>
                </StackItem>

                {isEditing && previewJson && (
                  <StackItem>
                    <Stack hasGutter>
                      <StackItem>
                        <Alert 
                          variant="info" 
                          title={`Preview & Edit: ${currentMockName}`}
                          isInline
                        >
                          Modify the JSON below and click "Send Modified JSON" to test your changes.
                        </Alert>
                      </StackItem>
                      <StackItem>
                        <TextArea
                          value={previewJson}
                          onChange={(_event, value) => {
                            setPreviewJson(value);
                            setJsonError('');
                          }}
                          rows={15}
                          className="mock-textarea-preview"
                        />
                      </StackItem>
                      {jsonError && (
                        <StackItem>
                          <Alert variant="danger" title="JSON Error" isInline>
                            {jsonError}
                          </Alert>
                        </StackItem>
                      )}
                      <StackItem>
                        <Stack hasGutter direction={{ default: 'row' }}>
                          <StackItem>
                            <Button variant="primary" onClick={validateAndSendPreviewJson}>
                              Send Modified JSON
                            </Button>
                          </StackItem>
                          <StackItem>
                            <Button variant="secondary" onClick={handleSendOriginal}>
                              Send Original
                            </Button>
                          </StackItem>
                          <StackItem>
                            <Button variant="link" onClick={() => setIsEditing(false)}>
                              Cancel
                            </Button>
                          </StackItem>
                        </Stack>
                      </StackItem>
                    </Stack>
                  </StackItem>
                )}

                <StackItem>
                  <Button
                    variant="link"
                    onClick={() => setShowCustomJson(!showCustomJson)}
                  >
                    {showCustomJson ? 'Hide' : 'Show'} Custom JSON Input
                  </Button>
                </StackItem>

                {showCustomJson && (
                  <StackItem>
                    <Stack hasGutter>
                      <StackItem>
                        <TextArea
                          value={customJson}
                          onChange={(_event, value) => {
                            onCustomJsonChange(value);
                            setJsonError('');
                          }}
                          placeholder='Paste custom component JSON here...'
                          rows={10}
                          className="mock-textarea-custom"
                        />
                      </StackItem>
                      {jsonError && (
                        <StackItem>
                          <Alert variant="danger" title="JSON Error" isInline>
                            {jsonError}
                          </Alert>
                        </StackItem>
                      )}
                      <StackItem>
                        <Button onClick={validateAndSendJson}>
                          Send Custom JSON
                        </Button>
                      </StackItem>
                    </Stack>
                  </StackItem>
                )}
              </>
            )}
    </Stack>
  );
};


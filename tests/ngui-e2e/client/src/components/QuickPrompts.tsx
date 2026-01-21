import React, { useState } from 'react';
import {
  Tabs,
  Tab,
  TabTitleText,
  Card,
  CardBody,
  CardTitle,
  Grid,
  GridItem,
  Stack,
  StackItem,
  Label
} from '@patternfly/react-core';
import { groupedPrompts } from '../quickPrompts';
import type { QuickPrompt, QuickPromptCategory } from '../quickPrompts';

interface QuickPromptsProps {
  onPromptSelect: (prompt: QuickPrompt) => void;
  disabled?: boolean;
}

export const QuickPrompts: React.FC<QuickPromptsProps> = ({ 
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

  const handlePromptClick = (prompt: QuickPrompt) => {
    onPromptSelect(prompt);
  };

  const renderPromptCard = (prompt: QuickPrompt) => (
    <GridItem key={prompt.id} span={6} sm={4} md={3}>
      <Card 
        isCompact 
        isSelectable 
        isClickable
        onClick={() => handlePromptClick(prompt)}
        className={`quick-prompt-card ${disabled ? 'quick-prompt-card-disabled' : 'quick-prompt-card-enabled'}`}
      >
        <CardTitle>
          <Stack>
            <StackItem>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                <Label color="blue" isCompact>
                  {prompt.expectedComponent === 'multiple' ? 'Multi' : prompt.expectedComponent}
                </Label>
                {prompt.tags && prompt.tags.length > 0 && (
                  <>
                    {prompt.tags.map((tag, index) => (
                      <Label 
                        key={index} 
                        color={tag === "Styled" ? "green" : "purple"} 
                        isCompact
                      >
                        {tag}
                      </Label>
                    ))}
                  </>
                )}
              </div>
            </StackItem>
          </Stack>
        </CardTitle>
        <CardBody>
          <Stack hasGutter>
            <StackItem>
              <strong className="quick-prompt-title">{prompt.prompt}</strong>
            </StackItem>
            <StackItem>
              <small 
                className="quick-prompt-id"
                title={prompt.id}
              >
                ID: {prompt.id}
              </small>
            </StackItem>
          </Stack>
        </CardBody>
      </Card>
    </GridItem>
  );

  const renderPromptsBySource = (category: QuickPromptCategory) => {
    const categoryPrompts = groupedPrompts[category];
    const generalPrompts = categoryPrompts.general || [];
    const k8sPrompts = categoryPrompts.k8s || [];

    return (
      <div className="test-panel-tab-content">
        <Stack hasGutter>
          {generalPrompts.length > 0 && (
            <StackItem>
              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#6a6e73' }}>
                  General ({generalPrompts.length})
                </h4>
                <Grid hasGutter>
                  {generalPrompts.map(renderPromptCard)}
                </Grid>
              </div>
            </StackItem>
          )}
          {k8sPrompts.length > 0 && (
            <StackItem>
              <div style={{ marginTop: generalPrompts.length > 0 ? '24px' : '0' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#6a6e73' }}>
                  Kubernetes / OpenShift ({k8sPrompts.length})
                </h4>
                <Grid hasGutter>
                  {k8sPrompts.map(renderPromptCard)}
                </Grid>
              </div>
            </StackItem>
          )}
        </Stack>
      </div>
    );
  };

  return (
    <Stack hasGutter>
      <StackItem>
        <small className="quick-prompts-hint">
          Click a prompt to test different component types through the LLM
        </small>
      </StackItem>
      <StackItem>
        <Tabs 
          activeKey={activeTabKey} 
          onSelect={handleTabClick}
          aria-label="Quick prompts tabs"
        >
                <Tab 
                  eventKey={0} 
                  title={<TabTitleText>🃎 One Card ({groupedPrompts['one-card'].general.length + groupedPrompts['one-card'].k8s.length})</TabTitleText>}
                  aria-label="One card prompts"
                >
                  {renderPromptsBySource('one-card')}
                </Tab>

                <Tab 
                  eventKey={1} 
                  title={<TabTitleText>🃏 Set Of Cards ({groupedPrompts['set-of-cards'].general.length + groupedPrompts['set-of-cards'].k8s.length})</TabTitleText>}
                  aria-label="Set of cards prompts"
                >
                  {renderPromptsBySource('set-of-cards')}
                </Tab>

                <Tab 
                  eventKey={2} 
                  title={<TabTitleText>📋 Tables ({groupedPrompts.tables.general.length + groupedPrompts.tables.k8s.length})</TabTitleText>}
                  aria-label="Tables prompts"
                >
                  {renderPromptsBySource('tables')}
                </Tab>

                <Tab 
                  eventKey={3} 
                  title={<TabTitleText>📊 Charts ({groupedPrompts.charts.general.length + groupedPrompts.charts.k8s.length})</TabTitleText>}
                  aria-label="Charts prompts"
                >
                  {renderPromptsBySource('charts')}
                </Tab>

                <Tab 
                  eventKey={4} 
                  title={<TabTitleText>🖼️ Image ({groupedPrompts['image'].general.length + groupedPrompts['image'].k8s.length})</TabTitleText>}
                  aria-label="Image prompts"
                >
                  {renderPromptsBySource('image')}
                </Tab>

                <Tab 
                  eventKey={5} 
                  title={<TabTitleText>🎥 Video Player ({groupedPrompts['video-player'].general.length + groupedPrompts['video-player'].k8s.length})</TabTitleText>}
                  aria-label="Video player prompts"
                >
                  {renderPromptsBySource('video-player')}
                </Tab>
        </Tabs>
      </StackItem>
    </Stack>
  );
};


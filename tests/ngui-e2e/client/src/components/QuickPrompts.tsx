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
import { quickPrompts, groupedPrompts } from '../quickPrompts';
import type { QuickPrompt, QuickPromptCategory } from '../quickPrompts';

interface QuickPromptsProps {
  onPromptSelect: (prompt: string) => void;
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
    onPromptSelect(prompt.prompt);
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
              <span className="quick-prompt-icon">{prompt.icon || '💬'}</span>
            </StackItem>
            <StackItem>
              <Label color="blue" isCompact>
                {prompt.expectedComponent === 'multiple' ? 'Multi' : prompt.expectedComponent}
              </Label>
            </StackItem>
          </Stack>
        </CardTitle>
        <CardBody>
          <Stack hasGutter>
            <StackItem>
              <strong className="quick-prompt-title">{prompt.prompt}</strong>
            </StackItem>
            <StackItem>
              <small className="quick-prompt-description">
                {prompt.description}
              </small>
            </StackItem>
          </Stack>
        </CardBody>
      </Card>
    </GridItem>
  );

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
                  title={<TabTitleText>🎴 Cards ({groupedPrompts.cards.length})</TabTitleText>}
                  aria-label="Cards prompts"
                >
                  <div className="test-panel-tab-content">
                    <Grid hasGutter>
                      {groupedPrompts.cards.map(renderPromptCard)}
                    </Grid>
                  </div>
                </Tab>

                <Tab 
                  eventKey={1} 
                  title={<TabTitleText>📋 Tables ({groupedPrompts.tables.length})</TabTitleText>}
                  aria-label="Tables prompts"
                >
                  <div className="test-panel-tab-content">
                    <Grid hasGutter>
                      {groupedPrompts.tables.map(renderPromptCard)}
                    </Grid>
                  </div>
                </Tab>

                <Tab 
                  eventKey={2} 
                  title={<TabTitleText>📊 Charts ({groupedPrompts.charts.length})</TabTitleText>}
                  aria-label="Charts prompts"
                >
                  <div className="test-panel-tab-content">
                    <Grid hasGutter>
                      {groupedPrompts.charts.map(renderPromptCard)}
                    </Grid>
                  </div>
                </Tab>

                <Tab 
                  eventKey={3} 
                  title={<TabTitleText>🎥 Media ({groupedPrompts.media.length})</TabTitleText>}
                  aria-label="Media prompts"
                >
                  <div className="test-panel-tab-content">
                    <Grid hasGutter>
                      {groupedPrompts.media.map(renderPromptCard)}
                    </Grid>
                  </div>
                </Tab>

                <Tab 
                  eventKey={4} 
                  title={<TabTitleText>🎭 Mixed ({groupedPrompts.mixed.length})</TabTitleText>}
                  aria-label="Mixed prompts"
                >
                  <div className="test-panel-tab-content">
                    <Grid hasGutter>
                      {groupedPrompts.mixed.map(renderPromptCard)}
                    </Grid>
                  </div>
                </Tab>
        </Tabs>
      </StackItem>
    </Stack>
  );
};


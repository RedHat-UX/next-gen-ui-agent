import {
  Chatbot,
  ChatbotContent,
  ChatbotDisplayMode,
  ChatbotFooter,
  ChatbotFootnote,
  ChatbotWelcomePrompt,
  Message,
  MessageBar,
  MessageBox,
  type MessageProps,
} from "@patternfly/chatbot";
import React, { useCallback, useRef, useState } from "react";

import DynamicComponent from "./DynamicComponent";
import { useFetch } from "../hooks/useFetch";
import { getMockDataByName } from "../mockData";
import { TestPanel } from "./TestPanel";
import { DebugSection } from "./DebugSection";
import type { QuickPrompt } from "../quickPrompts";
import { INLINE_DATASETS } from "../data/inlineDatasets";
import { useComponentHandlerRegistry } from '@rhngui/patternfly-react-renderer';
import { registerFormatters } from '../formatters/registerFormatters';
import { registerPromptTrigger } from '../handlers/promptTrigger';

export default function ChatBotPage() {
  const [messages, setMessages] = useState<MessageProps[]>([]);
  const [announcement] = useState<string>();
  const scrollToBottomRef = useRef<HTMLDivElement>(null);
  const isVisible = true;
  const displayMode = ChatbotDisplayMode.embedded; // Changed from fullscreen to embedded
  const position = "top";

  const { loading, fetchData } = useFetch();
  const registry = useComponentHandlerRegistry();

  // Register formatters for all data types
  React.useEffect(() => {
    return registerFormatters(registry);
  }, [registry]);

  // Check if debug mode is enabled via URL parameter
  const isDebugMode = React.useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('debug') === 'true';
  }, []);

  // Mock mode state
  const [isMockMode, setIsMockMode] = useState(false);
  const [selectedMock, setSelectedMock] = useState<string>('');
  const [customJson, setCustomJson] = useState('');
  
  // Model info state
  const [modelInfo, setModelInfo] = useState<{name: string, baseUrl: string} | undefined>();
  
  // Strategy selection state
  const [selectedStrategy, setSelectedStrategy] = useState<'one-step' | 'two-step'>('one-step');

  // Inline dataset (live mode) state - load from localStorage on mount
  const [inlineDataset, setInlineDataset] = useState(() => {
    try {
      return localStorage.getItem('ngui_inline_dataset') || '';
    } catch (e) {
      console.warn('Failed to load inline dataset from localStorage:', e);
      return '';
    }
  });
  const [inlineDatasetType, setInlineDatasetType] = useState(() => {
    try {
      return localStorage.getItem('ngui_inline_dataset_type') || '';
    } catch (e) {
      console.warn('Failed to load inline dataset type from localStorage:', e);
      return '';
    }
  });

  // Save to localStorage whenever values change
  React.useEffect(() => {
    try {
      if (inlineDataset) {
        localStorage.setItem('ngui_inline_dataset', inlineDataset);
      } else {
        localStorage.removeItem('ngui_inline_dataset');
      }
    } catch (e) {
      console.warn('Failed to save inline dataset to localStorage:', e);
    }
  }, [inlineDataset]);

  React.useEffect(() => {
    try {
      if (inlineDatasetType) {
        localStorage.setItem('ngui_inline_dataset_type', inlineDatasetType);
      } else {
        localStorage.removeItem('ngui_inline_dataset_type');
      }
    } catch (e) {
      console.warn('Failed to save inline dataset type to localStorage:', e);
    }
  }, [inlineDatasetType]);
  
  // Fetch model info on mount if in debug mode
  React.useEffect(() => {
    if (isDebugMode) {
      fetch(`${import.meta.env.VITE_API_ENDPOINT.replace('/generate', '')}/model-info`)
        .then(res => res.json())
        .then(data => setModelInfo(data))
        .catch(err => console.error('Failed to fetch model info:', err));
    }
  }, [isDebugMode]);
  
  // Resizable panel state
  const [panelWidth, setPanelWidth] = useState(600);
  const [isResizing, setIsResizing] = useState(false);
  const [isHoveringHandle, setIsHoveringHandle] = useState(false);
  const [isPanelCollapsed, setIsPanelCollapsed] = useState(false);

  // you will likely want to come up with your own unique id function; this is for demo purposes only
  const generateId = useCallback(() => {
    const id = Date.now() + Math.random();
    return id.toString();
  }, []);

  // Mock mode handlers
  const handleMockSend = (mockConfig: any, mockName: string) => {
    const newMessages: MessageProps[] = [...messages];
    const date = new Date();
    const messageId = generateId();
    
    newMessages.push({
      id: generateId(),
      role: 'user',
      content: `[MOCK] ${mockName}`,
      name: 'User',
      avatar: 'https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg',
      timestamp: date.toLocaleString(),
      avatarProps: { isBordered: true },
    });

    newMessages.push({
      id: messageId,
      role: 'bot',
      name: 'Bot',
      avatar: 'https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg',
      timestamp: date.toLocaleString(),
      extraContent: {
        afterMainContent: (
          <>
            <DynamicComponent config={mockConfig} showRawConfig={false} />
            {isDebugMode && <DebugSection config={mockConfig} messageId={messageId} />}
          </>
        ),
      },
    });

    setMessages(newMessages);
  };

  const handleMockSelect = (mockName: string) => {
    setSelectedMock(mockName);
    const mockConfig = getMockDataByName(mockName);
    if (mockConfig) {
      handleMockSend(mockConfig, mockName);
    }
  };

  const handleSendCustomJson = () => {
    try {
      if (!customJson || customJson.trim() === '') {
        console.error('No JSON to send');
        return;
      }
      const config = JSON.parse(customJson);
      // Check if this is a modified version of a selected mock
      const label = selectedMock ? `${selectedMock} (Modified)` : 'Custom JSON';
      handleMockSend(config, label);
    } catch (e) {
      console.error('Invalid JSON:', e);
    }
  };

  const handleSendMockDirect = (config: any, label: string) => {
    handleMockSend(config, label);
  };

  const handleQuickPromptSelect = (prompt: QuickPrompt) => {
    // If the prompt has a dataset, look it up by ID and attach it
    const dataset = prompt.dataset;
    if (dataset?.datasetId) {
      // Has a dataset ID - use inline data
      const inlineDataset = INLINE_DATASETS.find(d => d.id === dataset.datasetId);
      if (inlineDataset) {
        const datasetJson = JSON.stringify(inlineDataset.payload, null, 2);
        const datasetType = dataset.dataType || inlineDataset.dataType || '';
        // Update state for UI display
        setInlineDataset(datasetJson);
        setInlineDatasetType(datasetType);
        // Send the prompt with dataset override to avoid timing issues
        handleSend(prompt.prompt, datasetJson, datasetType);
      } else {
        console.warn(`Dataset with ID "${dataset.datasetId}" not found in INLINE_DATASETS`);
        // Fallback to sending without dataset
        setInlineDataset('');
        setInlineDatasetType('');
        handleSend(prompt.prompt);
      }
    } else {
      // No dataset (e.g., OpenShift queries using mock MCP server)
      // Tool names will automatically map to InputData.type
      setInlineDataset('');
      setInlineDatasetType('');
      // Send the prompt through normal flow
      handleSend(prompt.prompt);
    }
  };

  // Resize handlers
  const handleMouseDown = () => {
    setIsResizing(true);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (isResizing) {
      const newWidth = e.clientX;
      // Constrain width between 300px and 800px
      if (newWidth >= 300 && newWidth <= 800) {
        setPanelWidth(newWidth);
      }
    }
  };

  const handleMouseUp = () => {
    setIsResizing(false);
  };

  // Add/remove mouse event listeners
  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  const handleSend = useCallback(async (message: string, datasetOverride?: string, datasetTypeOverride?: string, toolNameOverride?: string) => {
    // Check if in mock mode
    if (isMockMode) {
      const newMessages: MessageProps[] = [...messages];
      const date = new Date();
      newMessages.push({
        id: generateId(),
        role: 'user',
        content: message,
        name: 'User',
        avatar: 'https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg',
        timestamp: date.toLocaleString(),
        avatarProps: { isBordered: true },
      });
      newMessages.push({
        id: generateId(),
        role: 'bot',
        name: 'Bot',
        content: 'Mock mode is enabled. Please select a mock component from the panel above.',
        avatar: 'https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg',
        timestamp: date.toLocaleString(),
      });
      setMessages(newMessages);
      return;
    }

    // Original live agent logic
    const newMessages: MessageProps[] = [];
    messages.forEach((message) => newMessages.push(message));
    const date = new Date();
    newMessages.push({
      id: generateId(),
      role: "user",
      content: message,
      name: "User",
      avatar:
        "https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg",
      timestamp: date.toLocaleString(),
      avatarProps: { isBordered: true },
    });
    newMessages.push({
      id: generateId(),
      role: "bot",
      content: "API response goes here",
      name: "Bot",
      isLoading: true,
      avatar:
        "https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg",
      timestamp: date.toLocaleString(),
    });
    setMessages(newMessages);

    // Use override dataset if provided, otherwise use state
    const datasetToUse = datasetOverride !== undefined ? datasetOverride : inlineDataset;
    const datasetTypeToUse = datasetTypeOverride !== undefined ? datasetTypeOverride : inlineDatasetType;
    // Use tool name override if provided, otherwise use dataset type
    const dataTypeToUse = toolNameOverride || datasetTypeToUse.trim() || undefined;

    // For OpenShift queries, don't send inline data - let the mock MCP server provide it
    // Tool names will automatically map to InputData.type via data_selection node
    const messageLower = message.toLowerCase();
    const isOpenShiftQuery = messageLower.includes("pod") || messageLower.includes("node");
    const shouldSendData = !isOpenShiftQuery && datasetToUse.trim();

    const res = await fetchData(import.meta.env.VITE_API_ENDPOINT, {
      method: "POST",
      body: { 
        prompt: message,
        strategy: selectedStrategy,
        ...(shouldSendData
          ? {
              data: datasetToUse,
              data_type: dataTypeToUse,
            }
          : {}),
      },
    });
    newMessages.pop();
    
    // Extract model info from metadata if available
    if (res?.metadata?.model) {
      setModelInfo(res.metadata.model);
    }
    
    
    const botMessageId = generateId();
    newMessages.push({
      id: botMessageId,
      role: "bot",
      name: "Bot",
      avatar:
        "https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg",
      timestamp: date.toLocaleString(),
      ...(!res
        ? { content: "Something went wrong!" }
        : res.error
        ? {
            content: `Error: ${res.error}${res.details ? ` - ${res.details}` : ''}`,
            extraContent: {
              afterMainContent: (
                <>
                  {isDebugMode && (res.metadata?.llmInteractions || res.metadata?.agentMessages) && (
                    <DebugSection
                      llmInteractions={res.metadata?.llmInteractions}
                      agentMessages={res.metadata?.agentMessages}
                      config={res.response}
                      messageId={botMessageId}
                    />
                  )}
                </>
              ),
            },
          }
        : {
            extraContent: {
              afterMainContent: (
                <>
                  <DynamicComponent 
                    config={res.response} 
                    showRawConfig={false}
                  />
                  {isDebugMode && (res.metadata || res.metadata?.llmInteractions || res.metadata?.agentMessages || res.metadata?.dataTransform || res.metadata?.dataset) && (
                    <DebugSection
                      metadata={res.metadata}
                      llmInteractions={res.metadata?.llmInteractions}
                      agentMessages={res.metadata?.agentMessages}
                      dataTransform={res.metadata?.dataTransform}
                      dataset={res.metadata?.dataset}
                      config={res.response}
                      messageId={botMessageId}
                    />
                  )}
                </>
              ),
            },
          }),
    });
    console.log(newMessages);
    setMessages(newMessages);
  }, [isMockMode, messages, inlineDataset, inlineDatasetType, selectedStrategy, fetchData, isDebugMode, generateId]);

  // Register prompt trigger callback so handlers can send prompts
  // This must be after handleSend is defined
  // Pass the current dataset and dataset type so the new prompt has access to the same data
  React.useEffect(() => {
    return registerPromptTrigger((prompt: string, dataset?: string, datasetType?: string, toolName?: string) => {
      // Use provided dataset/type if available, otherwise use current state
      const datasetToUse = dataset !== undefined ? dataset : inlineDataset;
      const datasetTypeToUse = datasetType !== undefined ? datasetType : inlineDatasetType;
      handleSend(prompt, datasetToUse, datasetTypeToUse, toolName);
    });
  }, [handleSend, inlineDataset, inlineDatasetType]);

  return (
    <div className="chatbot-layout">
      {/* Test Panel - Left Side (only shown when debug=true) */}
      {isDebugMode && (
        <div 
          className={`chatbot-panel ${isPanelCollapsed ? 'collapsed' : ''}`}
          style={{
            '--panel-width': isPanelCollapsed ? '60px' : `${panelWidth}px`
          } as React.CSSProperties}
        >
          <TestPanel
            isMockMode={isMockMode}
            onMockModeChange={setIsMockMode}
            selectedMock={selectedMock}
            onMockSelect={handleMockSelect}
            customJson={customJson}
            onCustomJsonChange={setCustomJson}
            onSendCustomJson={handleSendCustomJson}
            onSendMockDirect={handleSendMockDirect}
            onPromptSelect={handleQuickPromptSelect}
            disabled={loading}
            modelInfo={modelInfo}
            selectedStrategy={selectedStrategy}
            onStrategyChange={setSelectedStrategy}
            inlineDataset={inlineDataset}
            onInlineDatasetChange={setInlineDataset}
            inlineDatasetType={inlineDatasetType}
            onInlineDatasetTypeChange={setInlineDatasetType}
            isCollapsed={isPanelCollapsed}
            onToggleCollapse={() => setIsPanelCollapsed(!isPanelCollapsed)}
          />
        </div>
      )}

      {/* Resize Handle (only shown when debug=true and panel not collapsed) */}
      {isDebugMode && !isPanelCollapsed && (
        <div
          className={`chatbot-resize-handle ${isResizing ? 'is-dragging' : ''}`}
          onMouseDown={handleMouseDown}
          onMouseEnter={() => setIsHoveringHandle(true)}
          onMouseLeave={() => setIsHoveringHandle(false)}
        >
          {/* Visual indicator on the handle */}
          <div className="chatbot-resize-handle-indicator" />
        </div>
      )}

      {/* Chatbot - Takes full width when debug=false, right side when debug=true */}
      <div className="chatbot-content">
        <Chatbot displayMode={displayMode} isVisible={isVisible}>
          <ChatbotContent>
            {/* Update the announcement prop on MessageBox whenever a new message is sent
          so that users of assistive devices receive sufficient context  */}
            <MessageBox announcement={announcement} position={position}>
            {messages.length === 0 && (
              <ChatbotWelcomePrompt
                title="Hi, ChatBot User!"
                description="How can I help you today?"
              />
            )}
            {/* This code block enables scrolling to the top of the last message.
          You can instead choose to move the div with scrollToBottomRef on it below 
          the map of messages, so that users are forced to scroll to the bottom.
          If you are using streaming, you will want to take a different approach; 
          see: https://github.com/patternfly/chatbot/issues/201#issuecomment-2400725173 */}
            {messages && messages.map((message, index) => {
              if (index === messages.length - 1) {
                return (
                  <>
                    <div ref={scrollToBottomRef}></div>
                    <Message key={message.id} {...message} />
                  </>
                );
              }
              return <Message key={message.id} {...message} />;
            })}
          </MessageBox>
        </ChatbotContent>
        <ChatbotFooter>
          <MessageBar
            isAttachmentDisabled
            isSendButtonDisabled={loading}
            isCompact
            onSendMessage={(message: string | number) => handleSend(String(message))}
          />
          <ChatbotFootnote label="ChatBot uses AI. Check for mistakes." />
        </ChatbotFooter>
      </Chatbot>
      </div>
    </div>
  );
}

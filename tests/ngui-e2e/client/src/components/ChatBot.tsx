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
import React, { useRef, useState } from "react";

import DynamicComponent from "./DynamicComponent";
import { useFetch } from "../hooks/useFetch";
import { getMockDataByName } from "../mockData";
import { TestPanel } from "./TestPanel";
import { JsonViewer } from "./JsonViewer";
import { MetadataViewer } from "./MetadataViewer";
import { AgentMessagesViewer } from "./AgentMessagesViewer";

export default function ChatBotPage() {
  const [messages, setMessages] = useState<MessageProps[]>([]);
  const [announcement] = useState<string>();
  const scrollToBottomRef = useRef<HTMLDivElement>(null);
  const isVisible = true;
  const displayMode = ChatbotDisplayMode.embedded; // Changed from fullscreen to embedded
  const position = "top";

  const { loading, fetchData } = useFetch();

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

  // you will likely want to come up with your own unique id function; this is for demo purposes only
  const generateId = () => {
    const id = Date.now() + Math.random();
    return id.toString();
  };

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
            {isDebugMode && <JsonViewer config={mockConfig} messageId={messageId} />}
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
      setCustomJson(''); // Clear after sending
    } catch (e) {
      console.error('Invalid JSON:', e);
    }
  };

  const handleSendMockDirect = (config: any, label: string) => {
    handleMockSend(config, label);
  };

  const handleQuickPromptSelect = (prompt: string) => {
    // Send the prompt through normal flow
    handleSend(prompt);
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

  const handleSend = async (message: string) => {
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

    const res = await fetchData(import.meta.env.VITE_API_ENDPOINT, {
      method: "POST",
      body: { 
        prompt: message,
        strategy: selectedStrategy,
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
        ? { content: `Error: ${res.error}${res.details ? ` - ${res.details}` : ''}` }
        : {
            extraContent: {
              afterMainContent: (
                <>
                  <DynamicComponent config={res.response} showRawConfig={false} />
                  {isDebugMode && res.metadata && <MetadataViewer metadata={res.metadata} messageId={botMessageId} />}
                  {isDebugMode && res.metadata?.agentMessages && <AgentMessagesViewer messages={res.metadata.agentMessages} messageId={botMessageId} />}
                  {isDebugMode && <JsonViewer config={res.response} messageId={botMessageId} />}
                </>
              ),
            },
          }),
    });
    console.log(newMessages);
    setMessages(newMessages);
  };

  return (
    <div className="chatbot-layout">
      {/* Test Panel - Left Side (only shown when debug=true) */}
      {isDebugMode && (
        <div 
          className="chatbot-panel"
          style={{
            '--panel-width': `${panelWidth}px`
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
          />
        </div>
      )}

      {/* Resize Handle (only shown when debug=true) */}
      {isDebugMode && (
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

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
import { useRef, useState } from "react";

import DynamicComponent from "./DynamicComponent";
import { useFetch } from "../hooks/useFetch";

export default function ChatBotPage() {
  const [messages, setMessages] = useState<MessageProps[]>([]);
  const [announcement, setAnnouncement] = useState<string>();
  const scrollToBottomRef = useRef<HTMLDivElement>(null);
  const isVisible = true;
  const displayMode = ChatbotDisplayMode.fullscreen;
  const position = "top";

  const { loading, fetchData } = useFetch();

  // you will likely want to come up with your own unique id function; this is for demo purposes only
  const generateId = () => {
    const id = Date.now() + Math.random();
    return id.toString();
  };

  const handleSend = async (message: string) => {
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
      body: { prompt: message },
    });
    newMessages.pop();
    newMessages.push({
      id: generateId(),
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
              afterMainContent: <DynamicComponent config={res.response} showRawConfig={true} />,
            },
          }),
    });
    console.log(newMessages);
    setMessages(newMessages);
  };

  return (
    <>
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
            onSendMessage={handleSend}
          />
          <ChatbotFootnote label="ChatBot uses AI. Check for mistakes." />
        </ChatbotFooter>
      </Chatbot>
      {/* <DynamicComponent config={mockData} /> */}
    </>
  );
}

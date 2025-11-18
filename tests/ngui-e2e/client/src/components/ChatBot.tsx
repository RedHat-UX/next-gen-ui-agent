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
import {
  Button,
  Modal,
  ModalBody,
  ModalFooter,
  ModalHeader,
  TextArea,
  Form,
  FormGroup,
} from "@patternfly/react-core";
import { UploadIcon } from "@patternfly/react-icons";

export default function ChatBotPage() {
  const [messages, setMessages] = useState<MessageProps[]>([]);
  const [announcement] = useState<string>();
  const scrollToBottomRef = useRef<HTMLDivElement>(null);
  const isVisible = true;
  const displayMode = ChatbotDisplayMode.fullscreen;
  const position = "top";

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [finalJson, setFinalJson] = useState("");
  const [mockJsonData, setMockJsonData] = useState("");

  const handleModalToggle = () => {
    setIsModalOpen(!isModalOpen);
  };

  const handleSave = () => {
    setFinalJson(mockJsonData);
    setIsModalOpen(false);
  };

  const handleCancel = () => {
    setIsModalOpen(false);
    setMockJsonData("");
  };

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

    const res = await fetchData(
      import.meta.env.VITE_API_ENDPOINT + "/generate",
      {
        method: "POST",
        body: { prompt: message, mockJson: finalJson },
      }
    );
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
        ? {
            content: `Error: ${res.error}${
              res.details ? ` - ${res.details}` : ""
            }`,
          }
        : {
            extraContent: {
              afterMainContent: (
                <DynamicComponent config={res.response} showRawConfig={true} />
              ),
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
            {messages &&
              messages.map((message, index) => {
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
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              width: "100%",
            }}
          >
            <div style={{ flex: 1 }}>
              <MessageBar
                hasAttachButton={false}
                isSendButtonDisabled={loading}
                isCompact
                onSendMessage={(message: string | number) =>
                  handleSend(String(message))
                }
              />
            </div>
            <div>
              <Button
                variant="plain"
                aria-label="upload mock json"
                onClick={handleModalToggle}
                icon={<UploadIcon />}
              />
            </div>
          </div>
          <ChatbotFootnote label="ChatBot uses AI. Check for mistakes." />
        </ChatbotFooter>
      </Chatbot>
      <Modal isOpen={isModalOpen} onClose={handleCancel} variant="medium">
        <ModalHeader>Upload Mock JSON Data</ModalHeader>
        <ModalBody>
          <Form>
            <FormGroup label="Mock JSON" fieldId="mock-json-data">
              <TextArea
                value={mockJsonData}
                onChange={(_event, value) => setMockJsonData(value)}
                id="mock-json-data"
                rows={15}
                aria-label="Mock JSON Data"
              />
            </FormGroup>
          </Form>
        </ModalBody>
        <ModalFooter>
          <Button key="save" variant="primary" onClick={handleSave}>
            Save
          </Button>
          <Button key="cancel" variant="link" onClick={handleCancel}>
            Cancel
          </Button>
        </ModalFooter>
      </Modal>
    </>
  );
}

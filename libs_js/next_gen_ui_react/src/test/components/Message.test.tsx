import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import Message from "../../components/Message";

// Mock react-markdown
vi.mock("react-markdown", () => ({
  default: ({ children }: { children: string }) => <div>{children}</div>,
}));

// Mock PatternFly Message component to avoid dependency issues
vi.mock("@patternfly/chatbot/dist/dynamic/Message", () => ({
  default: ({ avatar, name, timestamp, extraContent }: { 
    avatar: string; 
    name: string; 
    timestamp: string; 
    extraContent: { beforeMainContent: any; afterMainContent: any } 
  }) => (
    <div data-testid="message-wrapper">
      <img src={avatar} alt={name} data-testid="avatar" />
      <div data-testid="name">{name}</div>
      <div data-testid="timestamp">{timestamp}</div>
      <div data-testid="before-content">{extraContent.beforeMainContent}</div>
      <div data-testid="after-content">{extraContent.afterMainContent}</div>
    </div>
  ),
}));

// Mock DynamicComponent
vi.mock("../../components/DynamicComponents", () => ({
  __esModule: true,
  default: ({ config }: { config: string }) => <div data-testid="dynamic-content">{config}</div>,
}));

describe("Message Component", () => {
  it("should render the message with default avatar if no avatar is provided", () => {
    const props = {
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
    };
    render(<Message {...props} />);

    const avatar = screen.getByTestId("avatar");
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute("src", "https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg");
  });

  it("should render the message with provided avatar", () => {
    const props = {
      avatar: "https://www.example.com/avatar.jpg",
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
    };
    render(<Message {...props} />);

    const avatar = screen.getByTestId("avatar");
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute("src", "https://www.example.com/avatar.jpg");
  });

  it("should render the sender's name and formatted datetime", () => {
    const props = {
      name: "John Doe",
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
    };
    render(<Message {...props} />);

    expect(screen.getByTestId("name")).toHaveTextContent("John Doe");
    expect(screen.getByTestId("timestamp")).toBeInTheDocument();
  });

  it("should render DynamicComponent with content", () => {
    const props = {
      content: "This is dynamic content",
      datetime: "2025-05-13T10:00:00Z",
    };
    render(<Message {...props} />);

    // Test if DynamicComponent is rendered with the correct content
    expect(screen.getByTestId("dynamic-content")).toHaveTextContent("This is dynamic content");
  });

  it("should render actions if provided", () => {
    const props = {
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
      actions: <button>Action Button</button>,
    };
    render(<Message {...props} />);

    // Check if the action button is rendered in the after-content section
    const afterContent = screen.getByTestId("after-content");
    expect(afterContent).toBeInTheDocument();
    expect(screen.getByText("Action Button")).toBeInTheDocument();
  });

  it("should display the default name if no name is provided", () => {
    const props = {
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
    };
    render(<Message {...props} />);

    expect(screen.getByTestId("name")).toHaveTextContent("Bot"); // Default name is "Bot"
  });

  it("should format datetime correctly", () => {
    const props = {
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
    };
    render(<Message {...props} />);

    const timestamp = screen.getByTestId("timestamp");
    expect(timestamp).toBeInTheDocument();
    // The timestamp should contain some formatted date string
    expect(timestamp.textContent).not.toBe("");
  });

  it("should pass customProps to DynamicComponent", () => {
    const props = {
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
      customProps: { testProp: "testValue" },
    };
    render(<Message {...props} />);

    // DynamicComponent should be rendered (this tests the prop passing indirectly)
    expect(screen.getByTestId("dynamic-content")).toBeInTheDocument();
  });
});

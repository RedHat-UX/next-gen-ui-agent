vi.mock("react-markdown");

import { render, screen } from "@testing-library/react";

import Message from "../../components/Message";

// Mocking DynamicComponent
vi.mock("../../components/DynamicComponents", () => ({
  __esModule: true,
  default: vi.fn(() => <div>Dynamic Content</div>),
}));

describe("Message Component", () => {
  it("should render the message with default avatar if no avatar is provided", () => {
    const props = {
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
    };
    render(<Message {...props} />);

    const avatar = screen.getByAltText("Bot");
    expect(avatar).toBeInTheDocument();
    expect(avatar.src).toBe(
      "https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg"
    );
  });

  it("should render the message with provided avatar", () => {
    const props = {
      avatar: "https://www.example.com/avatar.jpg",
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
    };
    render(<Message {...props} />);

    const avatar = screen.getByAltText("Bot");
    expect(avatar).toBeInTheDocument();
    expect(avatar.src).toBe("https://www.example.com/avatar.jpg");
  });

  it("should render the sender's name and formatted datetime", () => {
    const props = {
      name: "John Doe",
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
    };
    render(<Message {...props} />);

    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });

  it("should render DynamicComponent with content", () => {
    const props = {
      content: "This is dynamic content",
      datetime: "2025-05-13T10:00:00Z",
    };
    render(<Message {...props} />);

    // Test if DynamicComponent is rendered
    expect(screen.getByText("Dynamic Content")).toBeInTheDocument();
  });

  it("should render actions if provided", () => {
    const props = {
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
      actions: <button>Action Button</button>,
    };
    render(<Message {...props} />);

    // Check if the action button is rendered
    const actionButton = screen.getByText("Action Button");
    expect(actionButton).toBeInTheDocument();
  });

  it("should display the default name if no name is provided", () => {
    const props = {
      datetime: "2025-05-13T10:00:00Z",
      content: "Hello, world!",
    };
    render(<Message {...props} />);

    expect(screen.getByText("Bot")).toBeInTheDocument(); // Default name is "Bot"
  });
});

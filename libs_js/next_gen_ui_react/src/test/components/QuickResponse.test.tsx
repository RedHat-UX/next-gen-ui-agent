import { render, screen, fireEvent } from "@testing-library/react";
import { vi } from "vitest";

import QuickResponse from "../../components/QuickResponse";

// Mock the PatternFly Message component to avoid dependency issues
vi.mock("@patternfly/chatbot/dist/dynamic/Message", () => ({
  default: ({ content, quickResponses }: { content: string; quickResponses: Array<{ id: string; content: string; onClick: () => void }> }) => (
    <div>
      <div data-testid="message-content">{content}</div>
      <div data-testid="quick-responses">
        {quickResponses?.map((response) => (
          <button
            key={response.id}
            onClick={response.onClick}
            data-testid={`quick-response-${response.id}`}
          >
            {response.content}
          </button>
        ))}
      </div>
    </div>
  ),
}));

// Create a global mock function to test function execution
const mockGlobalFunction = vi.fn();
(globalThis as any).mockGlobalFunction = mockGlobalFunction;

describe("QuickResponse Component", () => {
  beforeEach(() => {
    mockGlobalFunction.mockClear();
  });

  it("renders the provided message", () => {
    const message = "This is a quick response message.";
    const actions = [
      { id: "action1", content: "Action 1", onClick: "mockGlobalFunction('action1')" },
    ];
    
    render(<QuickResponse message={message} actions={actions} />);
    
    const messageElement = screen.getByTestId("message-content");
    expect(messageElement).toBeInTheDocument();
    expect(messageElement).toHaveTextContent(message);
  });

  it("renders the correct number of buttons", () => {
    const actions = [
      { id: "action1", content: "Action 1", onClick: "mockGlobalFunction('action1')" },
      { id: "action2", content: "Action 2", onClick: "mockGlobalFunction('action2')" },
    ];
    
    render(<QuickResponse message="Test message" actions={actions} />);
    
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(actions.length);
  });

  it("renders the buttons with the correct labels", () => {
    const actions = [
      { id: "action1", content: "Action 1", onClick: "mockGlobalFunction('action1')" },
      { id: "action2", content: "Action 2", onClick: "mockGlobalFunction('action2')" },
    ];
    
    render(<QuickResponse message="Test message" actions={actions} />);
    
    const button1 = screen.getByText("Action 1");
    const button2 = screen.getByText("Action 2");
    expect(button1).toBeInTheDocument();
    expect(button2).toBeInTheDocument();
  });

  it("converts string onClick handlers to functions and executes them", () => {
    const actions = [
      { id: "action1", content: "Action 1", onClick: "mockGlobalFunction('action1')" },
    ];
    
    render(<QuickResponse message="Test message" actions={actions} />);
    
    const button = screen.getByText("Action 1");
    fireEvent.click(button);
    
    expect(mockGlobalFunction).toHaveBeenCalledWith('action1');
  });

  it("executes the correct onClick function for each button", () => {
    const actions = [
      { id: "action1", content: "Action 1", onClick: "mockGlobalFunction('action1')" },
      { id: "action2", content: "Action 2", onClick: "mockGlobalFunction('action2')" },
    ];
    
    render(<QuickResponse message="Test message" actions={actions} />);
    
    const button1 = screen.getByText("Action 1");
    const button2 = screen.getByText("Action 2");

    fireEvent.click(button1);
    fireEvent.click(button2);

    expect(mockGlobalFunction).toHaveBeenCalledWith('action1');
    expect(mockGlobalFunction).toHaveBeenCalledWith('action2');
    expect(mockGlobalFunction).toHaveBeenCalledTimes(2);
  });

  it("handles empty actions array", () => {
    render(<QuickResponse message="Test message" actions={[]} />);
    
    const messageElement = screen.getByTestId("message-content");
    expect(messageElement).toBeInTheDocument();
    expect(messageElement).toHaveTextContent("Test message");
    
    const buttons = screen.queryAllByRole("button");
    expect(buttons).toHaveLength(0);
  });

  it("handles function onClick handlers correctly", () => {
    const mockFn = vi.fn();
    const actions = [
      { id: "action1", content: "Action 1", onClick: mockFn },
    ];
    
    render(<QuickResponse message="Test message" actions={actions} />);
    
    const button = screen.getByText("Action 1");
    fireEvent.click(button);
    
    expect(mockFn).toHaveBeenCalledTimes(1);
  });
});

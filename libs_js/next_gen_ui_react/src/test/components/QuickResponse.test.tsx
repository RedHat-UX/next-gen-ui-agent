import { render, screen, fireEvent } from "@testing-library/react";
import { vi } from "vitest";

import QuickResponse from "../../components/QuickResponse";


// Mock ActionButton type
const mockAction = vi.fn();

const actions = [
  { label: "Action 1", onClick: mockAction },
  { label: "Action 2", onClick: mockAction },
];

describe("QuickResponse Component", () => {
  it("renders the provided message", () => {
    const message = "This is a quick response message.";
    render(<QuickResponse message={message} actions={actions} />);
    const messageElement = screen.getByText(message);
    expect(messageElement).toBeInTheDocument();
  });

  it("renders the correct number of buttons", () => {
    render(<QuickResponse message="Test message" actions={actions} />);
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(actions.length);
  });

  it("renders the buttons with the correct labels", () => {
    render(<QuickResponse message="Test message" actions={actions} />);
    const button1 = screen.getByText("Action 1");
    const button2 = screen.getByText("Action 2");
    expect(button1).toBeInTheDocument();
    expect(button2).toBeInTheDocument();
  });

  it("fires the onClick function when a button is clicked", () => {
    render(<QuickResponse message="Test message" actions={actions} />);
    const button1 = screen.getByText("Action 1");
    fireEvent.click(button1);
    expect(mockAction).toHaveBeenCalledTimes(1);
  });

  it("fires the correct onClick function for each button", () => {
    const mockAction1 = vi.fn();
    const mockAction2 = vi.fn();
    const actionsWithDifferentHandlers = [
      { label: "Action 1", onClick: mockAction1 },
      { label: "Action 2", onClick: mockAction2 },
    ];
    render(<QuickResponse message="Test message" actions={actionsWithDifferentHandlers} />);
    
    const button1 = screen.getByText("Action 1");
    const button2 = screen.getByText("Action 2");

    fireEvent.click(button1);
    fireEvent.click(button2);

    expect(mockAction1).toHaveBeenCalledTimes(1);
    expect(mockAction2).toHaveBeenCalledTimes(1);
  });
});

import { render, screen } from "@testing-library/react";

import MarkdownWrapper from "../../components/MarkdownWrapper";
import "@testing-library/jest-dom";

describe("MarkdownWrapper", () => {
  it("renders basic markdown", () => {
    const markdown = "# Hello World\nThis is **bold** text.";

    render(<MarkdownWrapper content={markdown} />);

    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Hello World");
    expect(screen.getByText("bold")).toBeInTheDocument();
    expect(screen.getByText("bold").tagName.toLowerCase()).toBe("strong");
  });

  it("renders GFM strikethrough and task list", () => {
    const markdown = `
  ~~Strikethrough~~
  
  - [x] Task 1
  - [ ] Task 2
  `;
  
    render(<MarkdownWrapper content={markdown} />);
  
    // ✅ Check strikethrough
    const strike = screen.getByText("Strikethrough");
    expect(strike).toBeInTheDocument();
    expect(strike.tagName.toLowerCase()).toBe("del");
  
    // ✅ Find list items first
    const taskItems = screen.getAllByRole("listitem");
  
    expect(taskItems).toHaveLength(2);
    expect(taskItems[0]).toHaveTextContent("Task 1");
    expect(taskItems[1]).toHaveTextContent("Task 2");
  
    // ✅ Find checkboxes inside list items
    const checkboxes = screen.getAllByRole("checkbox");
  
    expect(checkboxes).toHaveLength(2);
    expect(checkboxes[0]).toBeChecked();
    expect(checkboxes[1]).not.toBeChecked();
  });
  
  it("renders GFM table", () => {
    const markdown = `
| Name   | Age |
|--------|-----|
| Alice  | 25  |
| Bob    | 30  |
`;

    render(<MarkdownWrapper content={markdown} />);

    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("30")).toBeInTheDocument();
  });

  it("wraps content inside a div with markdown-content class", () => {
    const markdown = `# Header`;

    const { container } = render(<MarkdownWrapper content={markdown} />);
    const wrapper = container.querySelector(".markdown-content");

    expect(wrapper).toBeInTheDocument();
    expect(wrapper?.querySelector("h1")).toHaveTextContent("Header");
  });
});

import { render, screen } from "@testing-library/react";

import ListWrapper from "../../components/ListWrapper";
import "@testing-library/jest-dom";

describe("ListWrapper", () => {
  it("renders a flat list of strings", () => {
    render(<ListWrapper items={["Item 1", "Item 2"]} />);

    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("Item 2")).toBeInTheDocument();
  });

  it("renders list with nested subItems", () => {
    render(
      <ListWrapper
        items={[
          { label: "Parent 1", subItems: ["Child 1", "Child 2"] },
          "Standalone Item",
        ]}
      />
    );

    // Parent label
    expect(screen.getByText("Parent 1")).toBeInTheDocument();
    // Sub items
    expect(screen.getByText("Child 1")).toBeInTheDocument();
    expect(screen.getByText("Child 2")).toBeInTheDocument();
    // Flat item
    expect(screen.getByText("Standalone Item")).toBeInTheDocument();
  });

  it("renders with a different variant", () => {
    render(<ListWrapper variant="ol" items={["Ordered 1", "Ordered 2"]} />);

    const list = screen.getByRole("list"); // <ol> or <ul>
    expect(list.tagName.toLowerCase()).toBe("ol");
    expect(screen.getByText("Ordered 1")).toBeInTheDocument();
    expect(screen.getByText("Ordered 2")).toBeInTheDocument();
  });
});

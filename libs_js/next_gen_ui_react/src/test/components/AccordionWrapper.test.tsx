import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import AccordionWrapper from "../../components/AccordionWrapper";

describe("AccordionWrapper", () => {
  it("renders accordion items and toggles content", async () => {
    render(
      <AccordionWrapper
        items={[
          {
            id: "item1",
            title: "item 1",
            content: "Content 1",
          },
          {
            id: "item2",
            title: "item 2",
            content: "Content 2",
          },
          {
            id: "item3",
            title: "item 3",
            content: "Content 3",
          },
        ]}
      />
    );

    const item1 = screen.getByRole("button", { name: /item 1/i });
    const item2 = screen.getByRole("button", { name: /item 2/i });

    // Initially, content should be hidden
    expect(screen.queryByText("Content 1")).not.toBeVisible();
    expect(screen.queryByText("Content 2")).not.toBeVisible();

    // Click item 1
    await userEvent.click(item1);
    expect(screen.getByText("Content 1")).toBeVisible();

    // Click item 2, item 1 should collapse
    await userEvent.click(item2);
    expect(screen.getByText("Content 2")).toBeVisible();
    expect(screen.getByText("Content 1")).not.toBeVisible();
  });
});

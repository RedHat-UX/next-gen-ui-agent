import "@testing-library/jest-dom";

import { vi } from "vitest";

vi.mock("react-markdown", () => {
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => (
      <div>{children}</div>
    ),
  };
});

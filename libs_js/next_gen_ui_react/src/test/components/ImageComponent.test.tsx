import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";

import ImageComponent from "../../components/ImageComponent";

const mockImageData = {
  component: "image" as const,
  id: "test-id",
  image:
    "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
  title: "Toy Story Poster",
};

describe("ImageComponent", () => {
  const defaultProps = {
    component: "image" as const,
    id: mockImageData.id,
    image: mockImageData.image,
    title: mockImageData.title,
  };

  it("renders with required props", () => {
    render(<ImageComponent {...defaultProps} />);

    expect(screen.getByText("Toy Story Poster")).toBeInTheDocument();
    expect(
      screen.getByRole("img", { name: "Toy Story Poster" })
    ).toBeInTheDocument();
    expect(screen.getByRole("img")).toHaveAttribute("src", mockImageData.image);
  });

  it("renders image with correct attributes", () => {
    render(<ImageComponent {...defaultProps} />);

    const image = screen.getByRole("img");
    expect(image).toHaveAttribute("src", mockImageData.image);
    expect(image).toHaveAttribute("alt", "Toy Story Poster");
    expect(image).toHaveStyle("width: 100%");
    expect(image).toHaveStyle("height: auto");
    expect(image).toHaveStyle("object-fit: cover");
    expect(image).toHaveStyle(
      "border-radius: var(--pf-global--BorderRadius--sm)"
    );
  });

  it("applies correct card styling", () => {
    render(<ImageComponent {...defaultProps} />);

    const card = screen.getByRole("img").closest('[style*="max-width"]');
    expect(card).toHaveStyle("max-width: 400px");
  });

  it("applies custom id and className", () => {
    const customId = "custom-test-id";
    const customClassName = "custom-class";

    render(
      <ImageComponent
        {...defaultProps}
        id={customId}
        className={customClassName}
      />
    );

    const card = screen.getByRole("img").closest('[id="custom-test-id"]');
    expect(card).toBeInTheDocument();
    expect(card).toHaveClass(customClassName);
  });

  it("renders placeholder when image is null", () => {
    render(<ImageComponent {...defaultProps} image={null} />);

    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.getByText("No image provided")).toBeInTheDocument();

    const placeholder = screen.getByText("No image provided");
    expect(placeholder).toHaveStyle("width: 100%");
    expect(placeholder).toHaveStyle("height: 200px");
    expect(placeholder).toHaveStyle(
      "background-color: var(--pf-global--Color--200)"
    );
    expect(placeholder).toHaveStyle(
      "border-radius: var(--pf-global--BorderRadius--sm)"
    );
    expect(placeholder).toHaveStyle("display: flex");
    expect(placeholder).toHaveStyle("align-items: center");
    expect(placeholder).toHaveStyle("justify-content: center");
    expect(placeholder).toHaveStyle("color: var(--pf-global--Color--300)");
  });

  it("renders placeholder when image is undefined", () => {
    const { image: _image, ...propsWithoutImage } = defaultProps;
    void _image; // Acknowledge unused variable

    render(<ImageComponent {...propsWithoutImage} />);

    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.getByText("No image provided")).toBeInTheDocument();
  });

  it("renders placeholder when image is empty string", () => {
    render(<ImageComponent {...defaultProps} image="" />);

    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.getByText("No image provided")).toBeInTheDocument();
  });

  it("handles image load error", () => {
    render(<ImageComponent {...defaultProps} />);

    const image = screen.getByRole("img");
    expect(image).toBeInTheDocument();

    // Simulate image load error
    fireEvent.error(image);

    // After error, image should be hidden and error message should appear
    expect(image).toHaveStyle("display: none");

    // Check that error message is displayed
    const errorMessage = screen.getByText("Image failed to load");
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage).toHaveStyle("color: var(--pf-global--Color--200)");
    expect(errorMessage).toHaveStyle("text-align: center");
    expect(errorMessage).toHaveStyle("padding: 20px");
  });

  it("renders with different image URLs", () => {
    const testImageUrl = "https://example.com/test-image.jpg";

    render(<ImageComponent {...defaultProps} image={testImageUrl} />);

    const image = screen.getByRole("img");
    expect(image).toHaveAttribute("src", testImageUrl);
    expect(image).toHaveAttribute("alt", "Toy Story Poster");
  });

  it("renders with different titles", () => {
    const testTitle = "Different Movie Title";

    render(<ImageComponent {...defaultProps} title={testTitle} />);

    expect(screen.getByText(testTitle)).toBeInTheDocument();

    const image = screen.getByRole("img");
    expect(image).toHaveAttribute("alt", testTitle);
  });

  it("renders with different IDs", () => {
    const testId = "different-test-id";

    render(<ImageComponent {...defaultProps} id={testId} />);

    const card = screen.getByRole("img").closest('[id="different-test-id"]');
    expect(card).toBeInTheDocument();
  });

  it("handles very long titles", () => {
    const longTitle =
      "This is a very long title that might wrap to multiple lines and should still be displayed correctly";

    render(<ImageComponent {...defaultProps} title={longTitle} />);

    expect(screen.getByText(longTitle)).toBeInTheDocument();
  });

  it("handles special characters in title", () => {
    const specialTitle = "Movie Title with Special Characters: @#$%^&*()";

    render(<ImageComponent {...defaultProps} title={specialTitle} />);

    expect(screen.getByText(specialTitle)).toBeInTheDocument();

    const image = screen.getByRole("img");
    expect(image).toHaveAttribute("alt", specialTitle);
  });

  it("applies consistent styling across different scenarios", () => {
    const { rerender } = render(<ImageComponent {...defaultProps} />);

    // Test with image
    const image = screen.getByRole("img");
    expect(image).toHaveStyle("width: 100%");
    expect(image).toHaveStyle("height: auto");
    expect(image).toHaveStyle("object-fit: cover");

    // Test without image
    rerender(<ImageComponent {...defaultProps} image={null} />);
    const placeholder = screen.getByText("No image provided");
    expect(placeholder).toHaveStyle("width: 100%");
    expect(placeholder).toHaveStyle("height: 200px");
  });

  it("maintains accessibility with proper alt text", () => {
    render(<ImageComponent {...defaultProps} />);

    const image = screen.getByRole("img");
    expect(image).toHaveAttribute("alt", mockImageData.title);

    // Alt text should match the title
    expect(image.getAttribute("alt")).toBe("Toy Story Poster");
  });
});

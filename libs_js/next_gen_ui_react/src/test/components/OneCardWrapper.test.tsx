import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import OneCardWrapper from '../../components/OneCardWrapper';

const mockData = {
  component: "one-card",
  fields: [
    {
      data: ["Toy Story"],
      data_path: "movie.title",
      name: "Title"
    },
    {
      data: [1995],
      data_path: "movie.year",
      name: "Year"
    },
    {
      data: [8.3],
      data_path: "movie.imdbRating",
      name: "IMDB Rating"
    },
    {
      data: ["2022-11-02 00:00:00"],
      data_path: "movie.released",
      name: "Release Date"
    },
    {
      data: ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
      data_path: "actors[*]",
      name: "Actors"
    }
  ],
  id: "test-id",
  image: "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
  title: "Toy Story Details"
};

describe('OneCardWrapper', () => {
  const defaultProps = {
    title: mockData.title,
    fields: mockData.fields,
    image: mockData.image,
    id: mockData.id,
  };

  it('renders with required props', () => {
    render(<OneCardWrapper title="Test Title" fields={[]} />);
    
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('renders with all provided props', () => {
    render(<OneCardWrapper {...defaultProps} />);
    
    expect(screen.getByText('Toy Story Details')).toBeInTheDocument();
    expect(screen.getByRole('img', { name: 'Toy Story Details' })).toBeInTheDocument();
    expect(screen.getByRole('img')).toHaveAttribute('src', mockData.image);
  });

  it('renders fields correctly', () => {
    render(<OneCardWrapper {...defaultProps} />);
    
    // Check field names (terms)
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Year')).toBeInTheDocument();
    expect(screen.getByText('IMDB Rating')).toBeInTheDocument();
    expect(screen.getByText('Release Date')).toBeInTheDocument();
    expect(screen.getByText('Actors')).toBeInTheDocument();
    
    // Check field values (descriptions)
    expect(screen.getByText('Toy Story')).toBeInTheDocument();
    expect(screen.getByText('1995')).toBeInTheDocument();
    expect(screen.getByText('8.3')).toBeInTheDocument();
    expect(screen.getByText('2022-11-02 00:00:00')).toBeInTheDocument();
    expect(screen.getByText('Jim Varney, Tim Allen, Tom Hanks, Don Rickles')).toBeInTheDocument();
  });

  it('renders without image when image prop is not provided', () => {
    const { image: _image, ...propsWithoutImage } = defaultProps;
    void _image; // Acknowledge unused variable
    
    render(<OneCardWrapper {...propsWithoutImage} />);
    
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(screen.getByText('Toy Story Details')).toBeInTheDocument();
  });

  it('renders without image when image prop is null', () => {
    render(<OneCardWrapper {...defaultProps} image={null} />);
    
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(screen.getByText('Toy Story Details')).toBeInTheDocument();
  });

  it('applies correct image size styling', () => {
    const { rerender } = render(<OneCardWrapper {...defaultProps} imageSize="sm" />);
    
    let imageContainer = screen.getByRole('img').closest('[style*="flex-basis"]');
    expect(imageContainer).toHaveStyle('flex-basis: 15%');
    
    rerender(<OneCardWrapper {...defaultProps} imageSize="md" />);
    imageContainer = screen.getByRole('img').closest('[style*="flex-basis"]');
    expect(imageContainer).toHaveStyle('flex-basis: 20%');
    
    rerender(<OneCardWrapper {...defaultProps} imageSize="lg" />);
    imageContainer = screen.getByRole('img').closest('[style*="flex-basis"]');
    expect(imageContainer).toHaveStyle('flex-basis: 25%');
  });

  it('defaults to medium image size when imageSize is not specified', () => {
    render(<OneCardWrapper {...defaultProps} />);
    
    const imageContainer = screen.getByRole('img').closest('[style*="flex-basis"]');
    expect(imageContainer).toHaveStyle('flex-basis: 20%');
  });

  it('applies custom id and className', () => {
    const customId = 'custom-test-id';
    const customClassName = 'custom-class';
    
    render(<OneCardWrapper {...defaultProps} id={customId} className={customClassName} />);
    
    const card = screen.getByRole('img').closest('[id="custom-test-id"]');
    expect(card).toBeInTheDocument();
    expect(card).toHaveClass(customClassName);
  });

  it('handles null values in field data', () => {
    const fieldsWithNull = [
      {
        data: [null, "Valid Value"],
        data_path: "test.path",
        name: "Test Field"
      }
    ];
    
    render(<OneCardWrapper title="Test" fields={fieldsWithNull} />);
    
    expect(screen.getByText('N/A, Valid Value')).toBeInTheDocument();
  });

  it('handles empty fields array', () => {
    render(<OneCardWrapper title="Test Title" fields={[]} />);
    
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    // Should not crash and should render the title
  });

  it('handles boolean values in field data', () => {
    const fieldsWithBoolean = [
      {
        data: [true, false],
        data_path: "test.boolean",
        name: "Boolean Field"
      }
    ];
    
    render(<OneCardWrapper title="Test" fields={fieldsWithBoolean} />);
    
    expect(screen.getByText('true, false')).toBeInTheDocument();
  });

  it('handles mixed data types in field data', () => {
    const fieldsWithMixedTypes = [
      {
        data: ["string", 123, true, null],
        data_path: "test.mixed",
        name: "Mixed Field"
      }
    ];
    
    render(<OneCardWrapper title="Test" fields={fieldsWithMixedTypes} />);
    
    expect(screen.getByText('string, 123, true, N/A')).toBeInTheDocument();
  });

  it('applies correct card styling', () => {
    render(<OneCardWrapper {...defaultProps} />);
    
    const card = screen.getByRole('img').closest('[style*="max-width"]');
    expect(card).toHaveStyle('max-width: 1440px');
    expect(card).toHaveStyle('margin: 0 auto');
    expect(card).toHaveStyle('width: 100%');
  });

  it('renders image with correct attributes', () => {
    render(<OneCardWrapper {...defaultProps} />);
    
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', mockData.image);
    expect(image).toHaveAttribute('alt', 'Toy Story Details');
    expect(image).toHaveStyle('width: 100%');
    expect(image).toHaveStyle('height: auto');
    expect(image).toHaveStyle('object-fit: cover');
  });

  it('renders title with correct heading level', () => {
    render(<OneCardWrapper {...defaultProps} />);
    
    const title = screen.getByRole('heading', { level: 4 });
    expect(title).toHaveTextContent('Toy Story Details');
  });

  it('renders description list with correct structure', () => {
    render(<OneCardWrapper {...defaultProps} />);
    
    // Check that description list exists (it's a <dl> element)
    const dlElement = document.querySelector('dl');
    expect(dlElement).toBeInTheDocument();
    
    // Check that all field terms are present
    mockData.fields.forEach(field => {
      expect(screen.getByText(field.name)).toBeInTheDocument();
    });
  });
});

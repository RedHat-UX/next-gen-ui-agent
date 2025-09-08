import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import VideoPlayerWrapper from '../../components/VideoPlayerWrapper';

const mockVideoData = {
  id: "test-video",
  title: "Toy Story Trailer",
  video: "https://www.youtube.com/watch?v=v-PjgYDrg70",
  video_img: "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
};

describe('VideoPlayerWrapper', () => {
  const defaultProps = {
    title: mockVideoData.title,
    id: mockVideoData.id,
    video: mockVideoData.video,
    video_img: mockVideoData.video_img,
  };

  it('renders with required props only', () => {
    render(<VideoPlayerWrapper title="Test Video" />);
    
    expect(screen.getByText('Test Video')).toBeInTheDocument();
  });

  it('renders with all provided props', () => {
    render(<VideoPlayerWrapper {...defaultProps} />);
    
    expect(screen.getByText('Toy Story Trailer')).toBeInTheDocument();
    expect(screen.getByTitle('Toy Story Trailer')).toBeInTheDocument();
  });

  it('renders YouTube video iframe when video URL is provided', () => {
    render(<VideoPlayerWrapper {...defaultProps} />);
    
    const iframe = screen.getByTitle('Toy Story Trailer');
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute('src', expect.stringContaining('youtube.com/embed'));
    expect(iframe).toHaveAttribute('allowFullScreen');
  });

  it('renders YouTube video with correct embed URL', () => {
    render(<VideoPlayerWrapper {...defaultProps} />);
    
    const iframe = screen.getByTitle('Toy Story Trailer');
    expect(iframe.getAttribute('src')).toContain('https://www.youtube.com/embed/v-PjgYDrg70?rel=0');
  });

  it('renders YouTube video with autoplay when autoPlay is true', () => {
    render(<VideoPlayerWrapper {...defaultProps} autoPlay={true} />);
    
    const iframe = screen.getByTitle('Toy Story Trailer');
    expect(iframe.getAttribute('src')).toContain('&autoplay=1');
  });

  it('renders direct video element for non-YouTube URLs', () => {
    const directVideoProps = {
      ...defaultProps,
      video: "https://example.com/video.mp4"
    };
    
    render(<VideoPlayerWrapper {...directVideoProps} />);
    
    const video = screen.getByTitle('Toy Story Trailer');
    expect(video).toBeInTheDocument();
    expect(video.tagName).toBe('VIDEO');
    expect(video).toHaveAttribute('src', 'https://example.com/video.mp4');
    expect(video).toHaveAttribute('controls');
  });

  it('renders poster image when video is null', () => {
    const posterOnlyProps = {
      ...defaultProps,
      video: null
    };
    
    render(<VideoPlayerWrapper {...posterOnlyProps} />);
    
    const image = screen.getByAltText('Toy Story Trailer');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', mockVideoData.video_img);
    expect(screen.queryByTitle('Toy Story Trailer')).not.toBeInTheDocument();
  });

  it('renders poster image when video is undefined', () => {
    const posterOnlyProps = {
      ...defaultProps,
      video: undefined
    };
    
    render(<VideoPlayerWrapper {...posterOnlyProps} />);
    
    const image = screen.getByAltText('Toy Story Trailer');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', mockVideoData.video_img);
  });

  it('renders fallback content when neither video nor poster image is provided', () => {
    const noContentProps = {
      title: "Test Video",
      video: null,
      video_img: null
    };
    
    render(<VideoPlayerWrapper {...noContentProps} />);
    
    expect(screen.getByText('No video content available')).toBeInTheDocument();
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('applies custom id and className', () => {
    const customProps = {
      ...defaultProps,
      id: 'custom-video-id',
      className: 'custom-video-class'
    };
    
    render(<VideoPlayerWrapper {...customProps} />);
    
    const card = screen.getByTitle('Toy Story Trailer').closest('[id="custom-video-id"]');
    expect(card).toBeInTheDocument();
    expect(card).toHaveClass('custom-video-class');
  });

  it('applies correct card styling', () => {
    render(<VideoPlayerWrapper {...defaultProps} />);
    
    // Find the card element by looking for the one with the specific styling
    const card = document.querySelector('[style*="max-width: 1440px"]');
    expect(card).toBeInTheDocument();
    expect(card).toHaveStyle('max-width: 1440px');
    expect(card).toHaveStyle('margin: 0 auto');
    expect(card).toHaveStyle('width: 100%');
  });

  it('renders title with correct heading level', () => {
    render(<VideoPlayerWrapper {...defaultProps} />);
    
    const title = screen.getByRole('heading', { level: 4 });
    expect(title).toHaveTextContent('Toy Story Trailer');
  });

  it('handles YouTube short URLs (youtu.be)', () => {
    const shortUrlProps = {
      ...defaultProps,
      video: "https://youtu.be/v-PjgYDrg70"
    };
    
    render(<VideoPlayerWrapper {...shortUrlProps} />);
    
    const iframe = screen.getByTitle('Toy Story Trailer');
    expect(iframe.getAttribute('src')).toContain('https://www.youtube.com/embed/v-PjgYDrg70');
  });

  it('renders video element without controls when controls is false', () => {
    const noControlsProps = {
      ...defaultProps,
      video: "https://example.com/video.mp4",
      controls: false
    };
    
    render(<VideoPlayerWrapper {...noControlsProps} />);
    
    const video = screen.getByTitle('Toy Story Trailer');
    expect(video).not.toHaveAttribute('controls');
  });

  it('sets iframe attributes correctly for YouTube videos', () => {
    render(<VideoPlayerWrapper {...defaultProps} />);
    
    const iframe = screen.getByTitle('Toy Story Trailer');
    expect(iframe).toHaveAttribute('allow', expect.stringContaining('autoplay'));
    expect(iframe).toHaveAttribute('allow', expect.stringContaining('encrypted-media'));
    expect(iframe).toHaveAttribute('referrerPolicy', 'strict-origin-when-cross-origin');
  });

  it('applies responsive styling to YouTube iframe container', () => {
    render(<VideoPlayerWrapper {...defaultProps} />);
    
    const iframe = screen.getByTitle('Toy Story Trailer');
    const container = iframe.parentElement;
    
    expect(container).toHaveStyle('position: relative');
    expect(container).toHaveStyle('padding-bottom: 56.25%'); // 16:9 aspect ratio
    expect(container).toHaveStyle('overflow: hidden');
  });

  it('handles malformed YouTube URLs gracefully', () => {
    const malformedProps = {
      ...defaultProps,
      video: "https://youtube.com/malformed-url"
    };
    
    render(<VideoPlayerWrapper {...malformedProps} />);
    
    const iframe = screen.getByTitle('Toy Story Trailer');
    expect(iframe).toBeInTheDocument();
    // Should still render iframe but with original URL
    expect(iframe).toHaveAttribute('src', 'https://youtube.com/malformed-url');
  });

  it('renders poster image with correct attributes', () => {
    const posterOnlyProps = {
      ...defaultProps,
      video: null
    };
    
    render(<VideoPlayerWrapper {...posterOnlyProps} />);
    
    const image = screen.getByAltText('Toy Story Trailer');
    expect(image).toHaveAttribute('src', mockVideoData.video_img);
    expect(image).toHaveAttribute('alt', 'Toy Story Trailer');
    expect(image).toHaveStyle('max-width: 100%');
    expect(image).toHaveStyle('height: auto');
    expect(image).toHaveStyle('object-fit: cover');
  });

  it('handles empty title gracefully', () => {
    render(<VideoPlayerWrapper title="" />);
    
    expect(screen.getByRole('heading', { level: 4 })).toHaveTextContent('');
  });

  it('handles special characters in title', () => {
    const specialTitle = "Test Video: <Script>alert('test')</Script> & More";
    render(<VideoPlayerWrapper title={specialTitle} />);
    
    expect(screen.getByText(specialTitle)).toBeInTheDocument();
  });

  it('applies custom width and height to direct video elements', () => {
    const customSizeProps = {
      ...defaultProps,
      video: "https://example.com/video.mp4",
      width: "800px",
      height: "450px"
    };
    
    render(<VideoPlayerWrapper {...customSizeProps} />);
    
    const video = screen.getByTitle('Toy Story Trailer');
    expect(video).toHaveStyle('width: 800px');
    expect(video).toHaveStyle('height: 450px');
  });

  it('renders with default autoPlay and controls values', () => {
    const directVideoProps = {
      ...defaultProps,
      video: "https://example.com/video.mp4"
    };
    
    render(<VideoPlayerWrapper {...directVideoProps} />);
    
    const video = screen.getByTitle('Toy Story Trailer');
    expect(video).toHaveAttribute('controls');
    expect(video).not.toHaveAttribute('autoplay');
  });

  it('handles video_img being null when video is also null', () => {
    const emptyProps = {
      title: "Empty Video",
      video: null,
      video_img: null
    };
    
    render(<VideoPlayerWrapper {...emptyProps} />);
    
    expect(screen.getByText('No video content available')).toBeInTheDocument();
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });
});

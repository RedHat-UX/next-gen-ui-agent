import {
  Card,
  CardBody,
  CardTitle,
  Title,
} from "@patternfly/react-core";
import React from "react";

interface VideoPlayerProps {
  id?: string;
  title: string;
  video?: string | null;
  video_img?: string | null;
  className?: string;
  autoPlay?: boolean;
  controls?: boolean;
  width?: string | number;
  height?: string | number;
}

const VideoPlayerWrapper: React.FC<VideoPlayerProps> = ({
  id,
  title,
  video,
  video_img,
  className,
  autoPlay = false,
  controls = true,
  width = "100%",
  height = "auto",
}) => {
  // Extract video ID from YouTube URL for embedding
  const getYouTubeEmbedUrl = (url: string) => {
    // Match various YouTube URL formats
    let videoId = '';
    
    // Standard YouTube URL: https://www.youtube.com/watch?v=VIDEO_ID
    const standardMatch = url.match(/[?&]v=([^&\s]{11})/);
    if (standardMatch) {
      videoId = standardMatch[1];
    } else {
      // Short YouTube URL: https://youtu.be/VIDEO_ID
      const shortMatch = url.match(/youtu\.be\/([^?\s]{11})/);
      if (shortMatch) {
        videoId = shortMatch[1];
      }
    }
    
    if (videoId) {
      const autoPlayParam = autoPlay ? '&autoplay=1' : '';
      return `https://www.youtube.com/embed/${videoId}?rel=0${autoPlayParam}`;
    }
    return url;
  };

  // Check if URL is a YouTube video
  const isYouTubeUrl = (url: string) => {
    return url.includes('youtube.com') || url.includes('youtu.be');
  };

  const renderVideoContent = () => {
    if (video) {
      if (isYouTubeUrl(video)) {
        // YouTube video embedding
        return (
          <div 
            style={{ 
              position: 'relative', 
              paddingBottom: '56.25%', // 16:9 aspect ratio
              height: 0, 
              overflow: 'hidden', 
              maxWidth: '100%',
              background: '#000',
              borderRadius: 'var(--pf-global--BorderRadius--sm)'
            }}
          >
            <iframe
              title={title}
              src={getYouTubeEmbedUrl(video)}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                border: 0
              }}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerPolicy="strict-origin-when-cross-origin"
              allowFullScreen
            />
          </div>
        );
      } else {
        // Direct video file
        return (
          <video
            src={video}
            controls={controls}
            autoPlay={autoPlay}
            style={{
              width,
              height,
              maxWidth: '100%',
              borderRadius: 'var(--pf-global--BorderRadius--sm)'
            }}
            title={title}
          >
            Your browser does not support the video tag.
          </video>
        );
      }
    } else if (video_img) {
      // Show poster image when no video URL is provided
      return (
        <div style={{ textAlign: 'center' }}>
          <img
            src={video_img}
            alt={title}
            style={{
              maxWidth: '100%',
              height: 'auto',
              borderRadius: 'var(--pf-global--BorderRadius--sm)',
              objectFit: 'cover',
            }}
          />
        </div>
      );
    }

    // Fallback when neither video nor poster image is available
    return (
      <div 
        style={{ 
          textAlign: 'center', 
          padding: '2rem',
          backgroundColor: 'var(--pf-global--BackgroundColor--200)',
          borderRadius: 'var(--pf-global--BorderRadius--sm)',
          color: 'var(--pf-global--Color--200)'
        }}
      >
        No video content available
      </div>
    );
  };

  return (
    <Card 
      id={id} 
      className={className}
      style={{ 
        maxWidth: "1440px", 
        margin: "0 auto",
        width: "100%"
      }}
    >
      <CardTitle>
        <Title headingLevel="h4" size="lg">
          {title}
        </Title>
      </CardTitle>
      <CardBody>
        {renderVideoContent()}
      </CardBody>
    </Card>
  );
};

export default VideoPlayerWrapper;

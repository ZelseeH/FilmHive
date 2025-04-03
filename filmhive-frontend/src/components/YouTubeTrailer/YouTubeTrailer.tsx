// src/components/YouTubeTrailer/YouTubeTrailer.tsx
import React from 'react';
import { useYouTubeTrailer } from '../../hooks/useYouTubeTrailer';
import styles from './YouTubeTrailer.module.css';

interface YouTubeTrailerProps {
  url: string;
  title?: string;
}

const YouTubeTrailer: React.FC<YouTubeTrailerProps> = ({ url, title }) => {
  const { embedUrl, error } = useYouTubeTrailer(url);

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  if (!embedUrl) {
    return <div className={styles.noTrailer}>Brak dostępnego trailera</div>;
  }

  return (
    <div className={styles.trailerContainer}>
      <h3>{title || 'Trailer'}</h3>
      <div className={styles.responsiveEmbed}>
        <iframe
          width="560"
          height="315"
          src={embedUrl}
          title={title || "YouTube trailer"}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        ></iframe>
      </div>
    </div>
  );
};

export default YouTubeTrailer;

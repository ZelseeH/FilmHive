import React from 'react';
import styles from './YouTubeTrailer.module.css';

const YouTubeTrailer = ({ url, title }) => {
  const getEmbedUrl = (youtubeUrl) => {
    if (!youtubeUrl) return null;
    let videoId;

    // Format: https://www.youtube.com/watch?v=VIDEO_ID
    if (youtubeUrl.includes('youtube.com/watch')) {
      const urlParams = new URLSearchParams(new URL(youtubeUrl).search);
      videoId = urlParams.get('v');
    }
    // Format: https://youtu.be/VIDEO_ID
    else if (youtubeUrl.includes('youtu.be')) {
      videoId = youtubeUrl.split('/').pop();
    }
    // Format: https://www.youtube.com/embed/VIDEO_ID
    else if (youtubeUrl.includes('youtube.com/embed')) {
      videoId = youtubeUrl.split('/').pop();
    }

    if (!videoId) return null;

    return `https://www.youtube.com/embed/${videoId}`;
  };

  const embedUrl = getEmbedUrl(url);

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

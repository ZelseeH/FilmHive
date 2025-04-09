import React, { useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import styles from './MovieDetails.module.css';
import { useMovieDetails } from './hooks/useMovieDetails';
import YouTubeTrailer from './components/YouTubeTrailer/YouTubeTrailer';
import MovieHeaderSection from './components/MovieHeaderSection/MovieHeaderSection';
import MovieCastSection from './components/MovieCastSection/MovieCastSection';
import MovieActionPanel from './components/MovieActionPanel/MovieActionPanel';

interface LocationState {
    movieId?: number;
}

const MovieDetail: React.FC = () => {
    const { movieTitle } = useParams<{ movieTitle: string }>();
    const location = useLocation();
    const { movieId } = (location.state as LocationState) || {};

    const [showFullDescription, setShowFullDescription] = useState<boolean>(false);
    const [userRating, setUserRating] = useState<number>(0);

    const { movie, loading, error } = useMovieDetails(movieId, movieTitle);

    const handleRatingChange = (newRating: number) => {
        setUserRating(newRating);
    };

    if (loading) return <div className={styles['loading']}>Ładowanie szczegółów filmu...</div>;
    if (error) return <div className={styles['error']}>Błąd: {error}</div>;
    if (!movie) return <div className={styles['not-found']}>Film nie został znaleziony</div>;

    return (
        <div className={styles['movie-detail-container']}>
            <div className={styles['header-panel-container']}>
                <MovieHeaderSection
                    movie={movie}
                    onShowFullDescription={() => setShowFullDescription(true)}
                />
                <div className={styles['side-panel']}>
                    <MovieActionPanel
                        movieId={movie.id}
                        onRatingChange={handleRatingChange}
                    />
                </div>
            </div>

            <div className={styles['content-container']}>
                {movie.trailer_url && (
                    <section className={styles['trailer-section']}>
                        <h2 className={styles['section-title']}>Zwiastun</h2>
                        <YouTubeTrailer url={movie.trailer_url} />
                    </section>
                )}

                {movie.actors && movie.actors.length > 0 && (
                    <MovieCastSection actors={movie.actors} />
                )}
            </div>

            {showFullDescription && (
                <div className={styles['modal-backdrop']} onClick={() => setShowFullDescription(false)}>
                    <div className={styles['modal-content']} onClick={e => e.stopPropagation()}>
                        <button
                            className={styles['modal-close-btn']}
                            onClick={() => setShowFullDescription(false)}
                        >
                            ×
                        </button>
                        <h2>{movie.title} - Pełny opis</h2>
                        <p>{movie.description}</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MovieDetail;

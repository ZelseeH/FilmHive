import React, { useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import styles from './MovieDetails.module.css';
import { useMovieDetails } from './hooks/useMovieDetails';
import YouTubeTrailer from './components/YouTubeTrailer/YouTubeTrailer';
import MovieHeaderSection from './components/MovieHeaderSection/MovieHeaderSection';
import MovieCastSection from './components/MovieCastSection/MovieCastSection';
import MovieActionPanel from './components/MovieActionPanel/MovieActionPanel';
import AllMovieComments from './components/AllMovieComments/AllMovieComments';

// DODAJ TE IMPORTY:
import CommentSection from './components/CommentSection/CommentSection';

interface LocationState {
    movieId?: number;
}

const MovieDetail: React.FC = () => {
    const { movieTitle } = useParams<{ movieTitle: string }>();
    const { state } = useLocation();
    const locationState = state as LocationState | undefined;
    const movieId = locationState?.movieId;

    const [showFullDescription, setShowFullDescription] = useState<boolean>(false);
    const [userRating, setUserRating] = useState<number>(0);

    const { movie, loading, error } = useMovieDetails(movieId, movieTitle);

    const handleRatingChange = (newRating: number) => {
        setUserRating(newRating);
    };

    const toggleDescriptionModal = () => {
        setShowFullDescription((prev) => !prev);
    };

    if (loading) return <div className={styles['loading']}>Ładowanie szczegółów filmu...</div>;
    if (error) return <div className={styles['error']}>Błąd: {error}</div>;
    if (!movie) return <div className={styles['not-found']}>Film nie został znaleziony</div>;

    console.log('MovieDetail - movie object:', movie);
    console.log('MovieDetail - movie.release_date:', movie.release_date);

    return (
        <div className={styles['movie-detail-container']}>
            <div className={styles['header-panel-container']}>
                <MovieHeaderSection movie={movie} onShowFullDescription={toggleDescriptionModal} />
                <div className={styles['side-panel']}>
                    <MovieActionPanel
                        movieId={movie.id}
                        onRatingChange={handleRatingChange}
                        releaseDate={movie.release_date}
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

                {movie.actors?.length > 0 && <MovieCastSection actors={movie.actors} />}

                <section className={styles['comments-section']}>


                    {/* Istniejąca sekcja - wszystkie komentarze */}
                    <div className={styles['all-comments-section']}>
                        <AllMovieComments movieId={movie.id} />
                    </div>
                </section>
            </div>

            {showFullDescription && (
                <div
                    className={styles['modal-backdrop']}
                    onClick={toggleDescriptionModal}
                    role="dialog"
                    aria-labelledby="modal-title"
                >
                    <div className={styles['modal-content']} onClick={(e) => e.stopPropagation()}>
                        <button
                            className={styles['modal-close-btn']}
                            onClick={toggleDescriptionModal}
                            aria-label="Zamknij opis"
                        >
                            ×
                        </button>
                        <h2 id="modal-title">{movie.title} - Pełny opis</h2>
                        <p>{movie.description}</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MovieDetail;

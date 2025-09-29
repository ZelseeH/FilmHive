import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useUpcomingPremieres } from '../../hooks/useUpcomingPremieres';
import TrailerModal from '../../../Upcoming/components/TrailerModal/TrailerModal';
import { getYouTubeId, getYouTubeThumbnail } from '../../utils/youtubeUtils';
import { getPersonSlug } from '../../utils/personUtils';
import styles from './UpcomingPremieres.module.css';

interface TrailerSelection {
    url: string;
    title: string;
}

const UpcomingPremieres: React.FC = () => {
    const { movies, loading, error } = useUpcomingPremieres(5);
    const [selectedTrailer, setSelectedTrailer] = useState<TrailerSelection | null>(null);
    const [showArrows, setShowArrows] = useState(false);
    const navigate = useNavigate();
    const sliderRef = useRef<HTMLDivElement>(null);

    // Sprawdź czy potrzebne są strzałki
    useEffect(() => {
        const checkScrollability = () => {
            if (sliderRef.current) {
                const { scrollWidth, clientWidth } = sliderRef.current;
                setShowArrows(scrollWidth > clientWidth);
            }
        };

        // Sprawdź po załadowaniu i zmianie rozmiaru okna
        checkScrollability();
        window.addEventListener('resize', checkScrollability);

        return () => window.removeEventListener('resize', checkScrollability);
    }, [movies]);

    const scrollLeft = () => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: -300, behavior: 'smooth' });
        }
    };

    const scrollRight = () => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: 300, behavior: 'smooth' });
        }
    };

    if (loading) return <div className={styles.loading}>Ładowanie nadchodzących premier...</div>;
    if (error) return <div className={styles.error}>Błąd: {error}</div>;
    if (!movies.length) return <div className={styles.noMovies}>Brak nadchodzących premier z trailerami</div>;

    const handleTrailerClick = (e: React.MouseEvent, trailerUrl: string, title: string) => {
        e.stopPropagation();
        setSelectedTrailer({ url: trailerUrl, title });
    };

    const handleMovieClick = (movieId: number, movieTitle: string) => {
        const slug = getPersonSlug(movieTitle);
        navigate(`/movie/details/${slug}`, { state: { movieId } });
    };

    const closeTrailer = () => {
        setSelectedTrailer(null);
    };

    return (
        <section className={styles.container}>
            <h2 className={styles.title}>Nadchodzące premiery</h2>

            <div className={styles.sliderContainer}>
                {/* Pokazuj strzałki tylko gdy są potrzebne */}
                {showArrows && (
                    <button
                        className={`${styles.arrowButton} ${styles.arrowLeft}`}
                        onClick={scrollLeft}
                        aria-label="Poprzednie"
                    >
                        ❮
                    </button>
                )}

                <div
                    className={`${styles.sliderWrapper} ${!showArrows ? styles.centered : ''}`}
                    ref={sliderRef}
                >
                    {movies.map(movie => {
                        const youtubeId = getYouTubeId(movie.trailer_url);
                        const thumbnailUrl = youtubeId ? getYouTubeThumbnail(youtubeId) : null;

                        return (
                            <div
                                key={movie.id}
                                className={styles.card}
                                onClick={() => handleMovieClick(movie.id, movie.title)}
                            >
                                {/* Miniatura YouTube z przyciskiem Play */}
                                <div className={styles.thumbnailContainer}>
                                    {thumbnailUrl ? (
                                        <>
                                            <img
                                                src={thumbnailUrl}
                                                alt={`Trailer - ${movie.title}`}
                                                className={styles.thumbnail}
                                            />
                                            <button
                                                className={styles.playButton}
                                                onClick={(e) => handleTrailerClick(e, movie.trailer_url, movie.title)}
                                                aria-label={`Odtwórz trailer - ${movie.title}`}
                                            >
                                                ▶
                                            </button>
                                        </>
                                    ) : (
                                        <div className={styles.noThumbnail}>
                                            Brak podglądu
                                        </div>
                                    )}
                                </div>

                                {/* Informacje o filmie */}
                                <div className={styles.movieInfo}>
                                    <h3 className={styles.movieTitle}>{movie.title}</h3>
                                    <p className={styles.releaseDate}>
                                        Premiera: {new Date(movie.release_date).toLocaleDateString('pl-PL')}
                                    </p>
                                    {movie.days_until_release && movie.days_until_release > 0 && (
                                        <p className={styles.countdown}>
                                            Za {movie.days_until_release} dni
                                        </p>
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>

                {/* Pokazuj strzałki tylko gdy są potrzebne */}
                {showArrows && (
                    <button
                        className={`${styles.arrowButton} ${styles.arrowRight}`}
                        onClick={scrollRight}
                        aria-label="Następne"
                    >
                        ❯
                    </button>
                )}
            </div>

            <div className={styles.viewAllContainer}>
                <Link to="/upcoming" className={styles.viewAllLink}>
                    Zobacz wszystkie nadchodzące premiery →
                </Link>
            </div>

            {selectedTrailer && (
                <TrailerModal
                    isOpen={true}
                    onClose={closeTrailer}
                    trailerUrl={selectedTrailer.url}
                    movieTitle={selectedTrailer.title}
                />
            )}
        </section>
    );
};

export default UpcomingPremieres;

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { UpcomingMovie } from '../../services/upcomingMoviesService';
import { createSlug } from '../../../../utils/formatters';
import TrailerModal from '../TrailerModal/TrailerModal';
import styles from './UpcomingMovieItem.module.css';

interface UpcomingMovieItemProps {
    movie: UpcomingMovie;
}

const UpcomingMovieItem: React.FC<UpcomingMovieItemProps> = ({ movie }) => {
    const [showTrailer, setShowTrailer] = useState(false);

    const formatReleaseDate = (): string => {
        if (!movie.release_date) return 'Data nieznana';

        const releaseDate = new Date(movie.release_date);
        const today = new Date();
        const diffTime = releaseDate.getTime() - today.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        const formattedDate =
            movie.release_date_formatted || releaseDate.toLocaleDateString('pl-PL');

        if (diffDays > 0) {
            return `${formattedDate} (za ${diffDays} ${diffDays === 1 ? 'dzień' : 'dni'})`;
        }

        return formattedDate;
    };

    const handleTrailerClick = () => {
        if (movie.trailer_url) {
            setShowTrailer(true);
        }
    };

    const closeTrailer = () => {
        setShowTrailer(false);
    };

    return (
        <>
            <div className={styles.movieItemWrapper}>
                <div className={styles.movieItem}>
                    <div className={styles.moviePoster2}>
                        <Link to={`/movie/details/${createSlug(movie.title)}`} state={{ movieId: movie.id }}>
                            <img
                                src={movie.poster_url || '/placeholder-poster.jpg'}
                                alt={movie.title}
                                onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    target.src = '/placeholder-poster.jpg';
                                    target.onerror = null;
                                }}
                            />
                        </Link>
                        <div className={styles.releaseBadge}>
                            <span className={styles.releaseText}>PREMIERA</span>
                        </div>
                    </div>

                    <div className={styles.movieInfo}>
                        <div className={styles.movieHeader}>
                            <h3 className={styles.movieTitle}>
                                <Link to={`/movie/details/${createSlug(movie.title)}`} state={{ movieId: movie.id }}>
                                    {movie.title}
                                </Link>
                            </h3>
                            <p className={styles.movieOriginalTitle}>{formatReleaseDate()}</p>
                        </div>

                        <div className={styles.movieDetails}>
                            <p className={styles.movieWatchlist}>
                                <span>chcę obejrzeć</span>
                                <span className={styles.watchlistText}>👁 {movie.watchlist_count || 0}</span>
                            </p>
                            {movie.country && (
                                <p className={styles.movieCountry}>
                                    <span>kraj</span>
                                    <span className={styles.countryText}>{movie.country}</span>
                                </p>
                            )}
                        </div>

                        <div className={styles.trailerSection}>
                            {movie.trailer_url ? (
                                <button
                                    className={styles.trailerButton}
                                    onClick={handleTrailerClick}
                                >
                                    🎬 Zobacz zwiastun
                                </button>
                            ) : (
                                <div className={styles.noTrailer}>🎬 Brak zwiastuna</div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <TrailerModal
                isOpen={showTrailer}
                onClose={closeTrailer}
                trailerUrl={movie.trailer_url || ''}
                movieTitle={movie.title}
            />
        </>
    );
};

export default UpcomingMovieItem;

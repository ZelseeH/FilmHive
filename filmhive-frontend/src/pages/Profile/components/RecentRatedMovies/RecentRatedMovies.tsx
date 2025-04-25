import React, { useState } from "react";
import { Link } from "react-router-dom";
import { RecentRatedMovie } from "../../services/userMoviesService";
import { createSlug } from "../../../../utils/formatters";
import styles from "./RecentRatedMovies.module.css";
import StarRating from "../../../MovieDetails/components/StarRating/StarRating";
import CommentSection from "../../../MovieDetails/components/CommentSection/CommentSection";

interface Props {
    movies: RecentRatedMovie[];
    loading: boolean;
    error: string | null;
}

const RecentRatedMovies: React.FC<Props> = ({ movies, loading, error }) => {
    const [activeMovieId, setActiveMovieId] = useState<number | null>(null);
    const [isPopupHovered, setIsPopupHovered] = useState(false);

    if (loading) return <div>Ładowanie ocenionych filmów...</div>;
    if (error) return <div>Błąd: {error}</div>;
    if (!movies.length) return <div>Brak ocenionych filmów.</div>;

    const handleRatingHover = (movieId: number) => {
        setActiveMovieId(movieId);
    };

    const handleRatingLeave = () => {
        if (!isPopupHovered) {
            setActiveMovieId(null);
        }
    };

    const handlePopupMouseEnter = () => {
        setIsPopupHovered(true);
    };

    const handlePopupMouseLeave = () => {
        setIsPopupHovered(false);
        setActiveMovieId(null);
    };

    const stopPropagation = (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
    };

    return (
        <div className={styles.container}>
            <h3>Ostatnio ocenione filmy</h3>
            <div className={styles.moviesList}>
                {movies.map((movie) => (
                    <div key={movie.movie_id} className={styles.movieCardWrapper}>
                        <Link
                            to={`/movie/details/${createSlug(movie.title)}`}
                            state={{ movieId: movie.movie_id }}
                            className={styles.movieCard}
                            tabIndex={0}
                        >
                            <div className={styles.posterWrapper}>
                                <img
                                    src={movie.poster_url || "/default-poster.jpg"}
                                    alt={movie.title}
                                    className={styles.poster}
                                    draggable={false}
                                />
                                <span
                                    className={styles.ratingBadge}
                                    onMouseEnter={() => handleRatingHover(movie.movie_id)}
                                    onMouseLeave={handleRatingLeave}
                                >
                                    <span className={styles.star}>★</span>
                                    <span className={styles.ratingValue}>{movie.rating}</span>
                                </span>
                            </div>
                            <div className={styles.title}>{movie.title}</div>
                        </Link>

                        {activeMovieId === movie.movie_id && (
                            <div
                                className={styles.ratingPopup}
                                onMouseEnter={handlePopupMouseEnter}
                                onMouseLeave={handlePopupMouseLeave}
                                onClick={stopPropagation}
                            >
                                <div className={styles.ratingPopupContent}>
                                    <h4>Twoja ocena filmu {movie.title}</h4>
                                    <StarRating movieId={movie.movie_id} />
                                    <CommentSection movieId={movie.movie_id} />
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RecentRatedMovies;

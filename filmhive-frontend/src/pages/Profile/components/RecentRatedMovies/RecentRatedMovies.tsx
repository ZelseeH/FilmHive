import React from "react";
import { Link } from "react-router-dom";
import { RecentRatedMovie } from "../../services/userMoviesService";
import { createSlug } from "../../../../utils/formatters";
import styles from "./RecentRatedMovies.module.css";

interface Props {
    movies: RecentRatedMovie[];
    loading: boolean;
    error: string | null;
}

const RecentRatedMovies: React.FC<Props> = ({ movies, loading, error }) => {
    if (loading) return <div>Ładowanie ocenionych filmów...</div>;
    if (error) return <div>Błąd: {error}</div>;
    if (!movies.length) return <div>Brak ocenionych filmów.</div>;

    return (
        <div className={styles.container}>
            <h3>Ostatnio ocenione filmy</h3>
            <div className={styles.moviesList}>
                {movies.map((movie) => (
                    <Link
                        to={`/movie/details/${createSlug(movie.title)}`}
                        state={{ movieId: movie.movie_id }}
                        key={movie.movie_id}
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
                            <span className={styles.ratingBadge}>
                                <span className={styles.star}>★</span>
                                <span className={styles.ratingValue}>{movie.rating}</span>
                            </span>
                        </div>
                        <div className={styles.title}>{movie.title}</div>
                    </Link>
                ))}
            </div>
        </div>
    );
};

export default RecentRatedMovies;

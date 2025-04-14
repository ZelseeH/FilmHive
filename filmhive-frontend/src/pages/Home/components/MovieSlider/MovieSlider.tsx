import React, { useRef } from 'react';
import styles from './MovieSlider.module.css';
import MovieCard from '../MovieCard/MovieCard';

interface Movie {
    id: number;
    title: string;
    poster_url?: string;
    [key: string]: any;
}

interface UserRatings {
    [movieId: number]: number;
}

interface MovieSliderProps {
    movies: Movie[];
    selectedMovieId?: number;
    userRatings: UserRatings;
    onMovieSelect: (movie: Movie) => void;
}

const MovieSlider: React.FC<MovieSliderProps> = ({ movies, selectedMovieId, userRatings, onMovieSelect }) => {
    const sliderRef = useRef<HTMLDivElement>(null);

    const scrollLeft = () => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: -360, behavior: 'smooth' });
        }
    };

    const scrollRight = () => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: 360, behavior: 'smooth' });
        }
    };

    return (
        <div className={styles['movies-section']}>
            <div className={styles['movies-slider-container']}>
                <div className={`${styles['slider-arrow']} ${styles['left-arrow']}`} onClick={scrollLeft}>❮</div>
                <div className={styles['movies-slider']} ref={sliderRef}>
                    {movies.map((movie) => (
                        <MovieCard
                            key={movie.id}
                            movie={movie}
                            isActive={selectedMovieId === movie.id}
                            userRating={userRatings[movie.id]}
                            onClick={() => onMovieSelect(movie)}
                        />
                    ))}
                </div>
                <div className={`${styles['slider-arrow']} ${styles['right-arrow']}`} onClick={scrollRight}>❯</div>
            </div>
        </div>
    );
};

export default MovieSlider;

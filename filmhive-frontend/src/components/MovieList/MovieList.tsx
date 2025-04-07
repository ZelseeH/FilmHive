// src/components/MovieList/MovieList.tsx
import React, { useState, useEffect } from 'react';
import { useMovies } from '../../hooks/useMovies';
import Pagination from '../ui/Pagination';
import MovieItem from '../MovieItem/MovieItem';
import styles from './MovieList.module.css';


interface MovieListProps {

}

const MovieList: React.FC<MovieListProps> = () => {
    const [currentPage, setCurrentPage] = useState<number>(1);
    // Używamy hooka bez argumentu, zgodnie z jego aktualną definicją
    const { movies, loading, error, userRatings } = useMovies();
    const [paginatedMovies, setPaginatedMovies] = useState<Array<any>>([]);
    const [totalPages, setTotalPages] = useState<number>(1);

    // Stała określająca liczbę filmów na stronę
    const moviesPerPage = 10;

    // Efekt do obliczania paginacji po zmianie listy filmów lub strony
    useEffect(() => {
        if (movies.length > 0) {
            const indexOfLastMovie = currentPage * moviesPerPage;
            const indexOfFirstMovie = indexOfLastMovie - moviesPerPage;
            setPaginatedMovies(movies.slice(indexOfFirstMovie, indexOfLastMovie));
            setTotalPages(Math.ceil(movies.length / moviesPerPage));
        } else {
            setPaginatedMovies([]);
            setTotalPages(1);
        }
    }, [movies, currentPage]);

    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage);
        window.scrollTo(0, 0);
    };

    if (loading) {
        return <div className={styles.loading}>Ładowanie filmów...</div>;
    }

    if (error) {
        return <div className={styles.error}>Błąd: {error}</div>;
    }

    return (
        <div className={styles.movieListContainer}>
            {paginatedMovies.length > 0 ? (
                paginatedMovies.map(movie => (
                    <MovieItem
                        key={movie.id}
                        movie={movie}
                        userRating={userRatings[movie.id]}
                    />
                ))
            ) : (
                <div className={styles.noMovies}>Nie znaleziono filmów</div>
            )}

            {totalPages > 1 && (
                <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                />
            )}
        </div>
    );
};

export default MovieList;

// hooks/useMovies.ts
import { useState, useEffect } from 'react';

interface Movie {
    id: number;
    title: string;
    release_year: number;
    poster_path: string;
    rating: number;
    genres: string[];
}

interface Filters {
    title?: string;
    genres?: string;
    years?: string;
    rating?: string;
}

export const useMovies = (filters: Filters, page: number) => {
    const [movies, setMovies] = useState<Movie[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);

    useEffect(() => {
        const fetchMovies = async () => {
            try {
                setLoading(true);
                setError(null);

                // Tutaj będzie faktyczne pobieranie filmów z API z uwzględnieniem filtrów
                // Na razie symulujemy odpowiedź
                await new Promise(resolve => setTimeout(resolve, 800));

                // Przykładowe filmy
                const sampleMovies: Movie[] = Array.from({ length: 20 }, (_, i) => ({
                    id: i + 1,
                    title: `Film przykładowy ${i + 1}`,
                    release_year: 2000 + Math.floor(Math.random() * 23),
                    poster_path: 'https://via.placeholder.com/300x450',
                    rating: Math.floor(Math.random() * 5) + 5, // Ocena 5-10
                    genres: ['Akcja', 'Dramat', 'Komedia'].slice(0, Math.floor(Math.random() * 3) + 1)
                }));

                // Filtrowanie filmów na podstawie przekazanych filtrów
                let filteredMovies = [...sampleMovies];

                if (filters.title) {
                    filteredMovies = filteredMovies.filter(movie =>
                        movie.title.toLowerCase().includes(filters.title!.toLowerCase())
                    );
                }

                if (filters.genres) {
                    const genreList = filters.genres.split(',');
                    filteredMovies = filteredMovies.filter(movie =>
                        genreList.some(genre => movie.genres.includes(genre))
                    );
                }

                if (filters.years) {
                    const yearList = filters.years.split(',').map(Number);
                    filteredMovies = filteredMovies.filter(movie =>
                        yearList.includes(movie.release_year)
                    );
                }

                if (filters.rating) {
                    const minRating = parseInt(filters.rating);
                    filteredMovies = filteredMovies.filter(movie =>
                        movie.rating >= minRating
                    );
                }

                // Paginacja
                const itemsPerPage = 10;
                const start = (page - 1) * itemsPerPage;
                const paginatedMovies = filteredMovies.slice(start, start + itemsPerPage);

                setMovies(paginatedMovies);
                setTotalPages(Math.ceil(filteredMovies.length / itemsPerPage));
            } catch (err) {
                setError('Wystąpił błąd podczas pobierania filmów');
                console.error('Error fetching movies:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchMovies();
    }, [filters, page]);

    return { movies, loading, error, totalPages };
};

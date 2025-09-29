import { useState, useEffect } from 'react';
import { upcomingMoviesService } from '../services/upcomingMoviesService';
import type { UpcomingMovie, UpcomingMoviesResponse } from '../services/upcomingMoviesService';

interface UseUpcomingMoviesReturn {
    movies: UpcomingMovie[];
    loading: boolean;
    error: string | null;
    monthName: string;
    totalCount: number;
    refetch: () => void;
}

export const useUpcomingMovies = (year: number, month: number): UseUpcomingMoviesReturn => {
    const [movies, setMovies] = useState<UpcomingMovie[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [monthName, setMonthName] = useState<string>('');
    const [totalCount, setTotalCount] = useState<number>(0);

    const fetchUpcomingMovies = async () => {
        const validation = upcomingMoviesService.validateYearMonth(year, month);
        if (!validation.isValid) {
            setError(validation.error || 'Nieprawidłowe parametry');
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const data: UpcomingMoviesResponse = await upcomingMoviesService.getUpcomingMoviesByMonth(year, month);

            setMovies(data.movies);
            setMonthName(data.month_name);
            setTotalCount(data.total_count);

        } catch (err) {
            console.error('Error fetching upcoming movies:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił błąd podczas pobierania filmów');
            setMovies([]);
            setMonthName('');
            setTotalCount(0);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUpcomingMovies();
    }, [year, month]);

    const refetch = () => {
        fetchUpcomingMovies();
    };

    return {
        movies,
        loading,
        error,
        monthName,
        totalCount,
        refetch
    };
};

export const useCurrentMonthUpcomingMovies = (): UseUpcomingMoviesReturn => {
    const [movies, setMovies] = useState<UpcomingMovie[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [monthName, setMonthName] = useState<string>('');
    const [totalCount, setTotalCount] = useState<number>(0);

    const fetchCurrentMonthMovies = async () => {
        setLoading(true);
        setError(null);

        try {
            const data: UpcomingMoviesResponse = await upcomingMoviesService.getCurrentMonthUpcomingMovies();

            setMovies(data.movies);
            setMonthName(data.month_name);
            setTotalCount(data.total_count);

        } catch (err) {
            console.error('Error fetching current month upcoming movies:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił błąd podczas pobierania filmów');
            setMovies([]);
            setMonthName('');
            setTotalCount(0);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCurrentMonthMovies();
    }, []);

    const refetch = () => {
        fetchCurrentMonthMovies();
    };

    return {
        movies,
        loading,
        error,
        monthName,
        totalCount,
        refetch
    };
};

export const useUpcomingMoviesSelector = () => {
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth() + 1;

    const [selectedYear, setSelectedYear] = useState<number>(currentYear);
    const [selectedMonth, setSelectedMonth] = useState<number>(currentMonth);

    const { movies, loading, error, monthName, totalCount, refetch } = useUpcomingMovies(selectedYear, selectedMonth);

    const handleYearChange = (year: number) => {
        setSelectedYear(year);
    };

    const handleMonthChange = (month: number) => {
        setSelectedMonth(month);
    };

    const resetToCurrentMonth = () => {
        setSelectedYear(currentYear);
        setSelectedMonth(currentMonth);
    };

    return {
        selectedYear,
        selectedMonth,
        currentYear,
        currentMonth,
        movies,
        loading,
        error,
        monthName,
        totalCount,
        handleYearChange,
        handleMonthChange,
        resetToCurrentMonth,
        refetch
    };
};

export const useUpcomingMovieDetails = (movieId: number | null) => {
    const [movie, setMovie] = useState<UpcomingMovie | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!movieId) {
            setMovie(null);
            setError(null);
            return;
        }

        const fetchMovieDetails = async () => {
            setLoading(true);
            setError(null);

            try {
                const movieData = await upcomingMoviesService.getUpcomingMovieDetails(movieId);
                setMovie(movieData);
            } catch (err) {
                console.error('Error fetching upcoming movie details:', err);
                setError(err instanceof Error ? err.message : 'Wystąpił błąd podczas pobierania filmu');
                setMovie(null);
            } finally {
                setLoading(false);
            }
        };

        fetchMovieDetails();
    }, [movieId]);

    return {
        movie,
        loading,
        error
    };
};

export default {
    useUpcomingMovies,
    useCurrentMonthUpcomingMovies,
    useUpcomingMoviesSelector,
    useUpcomingMovieDetails
};

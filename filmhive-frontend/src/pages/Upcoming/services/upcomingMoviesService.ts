import { fetchWithAuth } from '../../../services/api';

export interface UpcomingMovie {
    id: number;
    movie_id?: number;
    title: string;
    original_title?: string;
    poster_url?: string;
    release_date?: string;
    release_date_formatted?: string;
    days_until_release?: number;
    description?: string;
    duration_minutes?: number;
    genres?: { id: number; name: string }[];
    actors?: { id: number; name: string }[];
    directors?: { name: string }[];
    country?: string;
    original_language?: string;
    trailer_url?: string;
    watchlist_count?: number;
}

export interface UpcomingMoviesResponse {
    movies: UpcomingMovie[];
    year: number;
    month: number;
    month_name: string;
    total_count: number;
}

export interface MonthOption {
    number: number;
    name: string;
    shortName: string;
}

export const getUpcomingMoviesByMonth = async (
    year: number,
    month: number
): Promise<UpcomingMoviesResponse> => {
    try {
        const response = await fetchWithAuth(
            `movies/upcoming/${year}/${month}`
        );

        return response;
    } catch (error) {
        console.error('Error fetching upcoming movies:', error);
        throw error instanceof Error
            ? error
            : new Error('Wystąpił błąd podczas pobierania nadchodzących premier');
    }
};

export const getCurrentMonthUpcomingMovies = async (): Promise<UpcomingMoviesResponse> => {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;

    return getUpcomingMoviesByMonth(currentYear, currentMonth);
};

export const getNextMonthUpcomingMovies = async (): Promise<UpcomingMoviesResponse> => {
    const now = new Date();
    let nextMonth = now.getMonth() + 2;
    let nextYear = now.getFullYear();

    if (nextMonth > 12) {
        nextMonth = 1;
        nextYear += 1;
    }

    return getUpcomingMoviesByMonth(nextYear, nextMonth);
};

export const getUpcomingMovieDetails = async (movieId: number): Promise<UpcomingMovie> => {
    try {
        const response = await fetchWithAuth(
            `movies/${movieId}?include_roles=true`
        );

        return response;
    } catch (error) {
        console.error(`Error fetching upcoming movie with id ${movieId}:`, error);
        throw error;
    }
};

export const validateYearMonth = (year: number, month: number): { isValid: boolean; error?: string } => {
    if (!Number.isInteger(year) || year < 1900 || year > 2100) {
        return {
            isValid: false,
            error: 'Rok musi być liczbą całkowitą między 1900 a 2100'
        };
    }

    if (!Number.isInteger(month) || month < 1 || month > 12) {
        return {
            isValid: false,
            error: 'Miesiąc musi być liczbą całkowitą między 1 a 12'
        };
    }

    return { isValid: true };
};

export const formatReleaseDate = (dateString: string): string => {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('pl-PL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (error) {
        return 'Data nieznana';
    }
};

export const calculateDaysUntilRelease = (releaseDate: string): number | null => {
    try {
        const release = new Date(releaseDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const diffTime = release.getTime() - today.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        return diffDays > 0 ? diffDays : null;
    } catch (error) {
        return null;
    }
};

export const formatDaysUntilRelease = (days: number): string => {
    if (days === 1) return '1 dzień';
    if (days < 5) return `${days} dni`;
    return `${days} dni`;
};

export const getAvailableYears = (): number[] => {
    const currentYear = new Date().getFullYear();
    return Array.from({ length: 4 }, (_, i) => currentYear + i);
};

export const getMonthsList = (): MonthOption[] => {
    return [
        { number: 1, name: 'Styczeń', shortName: 'Sty' },
        { number: 2, name: 'Luty', shortName: 'Lut' },
        { number: 3, name: 'Marzec', shortName: 'Mar' },
        { number: 4, name: 'Kwiecień', shortName: 'Kwi' },
        { number: 5, name: 'Maj', shortName: 'Maj' },
        { number: 6, name: 'Czerwiec', shortName: 'Cze' },
        { number: 7, name: 'Lipiec', shortName: 'Lip' },
        { number: 8, name: 'Sierpień', shortName: 'Sie' },
        { number: 9, name: 'Wrzesień', shortName: 'Wrz' },
        { number: 10, name: 'Październik', shortName: 'Paź' },
        { number: 11, name: 'Listopad', shortName: 'Lis' },
        { number: 12, name: 'Grudzień', shortName: 'Gru' }
    ];
};

export const getMonthName = (monthNumber: number): string => {
    const months = getMonthsList();
    const month = months.find(m => m.number === monthNumber);
    return month ? month.name : 'Nieznany miesiąc';
};

export const isUpcomingMovie = (releaseDate: string): boolean => {
    try {
        const release = new Date(releaseDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        return release.getTime() > today.getTime();
    } catch (error) {
        return false;
    }
};

export const upcomingMoviesService = {
    getUpcomingMoviesByMonth,
    getCurrentMonthUpcomingMovies,
    getNextMonthUpcomingMovies,
    getUpcomingMovieDetails,
    validateYearMonth,
    formatReleaseDate,
    calculateDaysUntilRelease,
    formatDaysUntilRelease,
    getAvailableYears,
    getMonthsList,
    getMonthName,
    isUpcomingMovie
};

export default upcomingMoviesService;

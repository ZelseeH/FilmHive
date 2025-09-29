export interface Movie {
    id: number;
    movie_id?: number;
    title: string;
    original_title?: string;
    poster_url?: string;
    release_date?: string;
    description?: string;
    duration_minutes?: number;
    genres?: { id: number; name: string }[];
    actors?: { id: number; name: string }[];
    directors?: { id: number; name: string }[];
    country?: string;
    original_language?: string;  // ✅ Też brakuje!
    trailer_url?: string;        // ✅ DODAJ TO POLE!
}


interface MoviesResponse {
    movies: Movie[];
    pagination: {
        page: number;
        total_pages: number;
        total: number;
        per_page: number;
        has_next: boolean;
        has_prev: boolean;
    };
}

const getAuthToken = (): string | null => {
    return localStorage.getItem('accessToken');
};

// Dodaj cache-busting headers
const getHeaders = (includeAuth: boolean = false) => {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    };

    if (includeAuth) {
        const token = getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

    return headers;
};

export const getMovies = async (
    filter: string = '',
    page: number = 1,
    perPage: number = 10
): Promise<MoviesResponse> => {
    try {
        let url = `http://localhost:5000/api/movies/getall?page=${page}&per_page=${perPage}`;

        if (filter && filter.trim()) {
            url += `&title=${encodeURIComponent(filter)}`;
        }

        // Dodaj timestamp dla cache-busting
        url += `&_t=${Date.now()}`;

        const response = await fetch(url, {
            headers: getHeaders()
        });

        if (!response.ok) {
            throw new Error('Nie udało się pobrać filmów');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching movies:', error);
        throw error;
    }
};

export const getMovieById = async (id: number): Promise<Movie> => {
    try {
        // Dodaj timestamp dla cache-busting
        const url = `http://localhost:5000/api/movies/${id}?_t=${Date.now()}`;

        const response = await fetch(url, {
            headers: getHeaders()
        });

        if (!response.ok) {
            throw new Error('Nie udało się pobrać danych filmu');
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching movie with id ${id}:`, error);
        throw error;
    }
};

export const updateMovie = async (movieId: number, movieData: FormData): Promise<Movie> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`http://localhost:5000/api/movies/${movieId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            },
            body: movieData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się zaktualizować filmu');
        }

        const data = await response.json();
        return data.movie || data;
    } catch (error) {
        console.error(`Error updating movie ${movieId}:`, error);
        throw error;
    }
};

export const uploadMoviePoster = async (movieId: number, posterFile: File): Promise<Movie> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const formData = new FormData();
        formData.append('poster', posterFile);

        const response = await fetch(`http://localhost:5000/api/movies/${movieId}/poster`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się zaktualizować plakatu');
        }

        const data = await response.json();
        return data.movie || data;
    } catch (error) {
        console.error(`Error uploading poster for movie ${movieId}:`, error);
        throw error;
    }
};

export const createMovie = async (movieData: FormData): Promise<Movie> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        // Konwertuj FormData na obiekt JSON - bez iteracji entries()
        const data: any = {};

        // Użyj forEach zamiast for...of
        movieData.forEach((value, key) => {
            if (key !== 'poster') { // Plakat pomijamy - backend nie obsługuje go w tym endpoincie
                data[key] = value;
            }
        });

        const response = await fetch(`http://localhost:5000/api/movies/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się utworzyć filmu');
        }

        const newMovie = await response.json();

        // Jeśli jest plakat, prześlij go osobno po utworzeniu filmu
        const posterFile = movieData.get('poster') as File;
        if (posterFile && posterFile.size > 0) {
            try {
                const updatedMovie = await uploadMoviePoster(newMovie.id, posterFile);
                return updatedMovie;
            } catch (posterError) {
                console.warn('Film został utworzony, ale nie udało się przesłać plakatu:', posterError);
                return newMovie;
            }
        }

        return newMovie;
    } catch (error) {
        console.error('Error creating movie:', error);
        throw error;
    }
};



export const deleteMovie = async (movieId: number): Promise<void> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`http://localhost:5000/api/movies/${movieId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się usunąć filmu');
        }
    } catch (error) {
        console.error(`Error deleting movie ${movieId}:`, error);
        throw error;
    }
};

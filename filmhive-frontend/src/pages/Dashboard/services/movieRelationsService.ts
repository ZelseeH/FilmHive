const getAuthToken = (): string | null => {
    return localStorage.getItem('accessToken');
};

export interface MovieActor {
    id: number;
    name: string;
    role?: string;
    photo_url?: string;
}

export interface MovieDirector {
    id: number;
    name: string;
    photo_url?: string;
}

export interface MovieGenre {
    genre_id: number;
    genre_name: string;
}

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

// AKTORZY - używamy tego samego endpointu co w MovieDetails
export const addActorToMovie = async (movieId: number, actorId: number, role: string = ''): Promise<void> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`http://localhost:5000/api/movie-relations/movies/${movieId}/actors`, {
            method: 'POST',
            headers: getHeaders(true),
            body: JSON.stringify({ actor_id: actorId, role })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się dodać aktora do filmu');
        }
    } catch (error) {
        console.error('Error adding actor to movie:', error);
        throw error;
    }
};

export const removeActorFromMovie = async (movieId: number, actorId: number): Promise<void> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`http://localhost:5000/api/movie-relations/movies/${movieId}/actors/${actorId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się usunąć aktora z filmu');
        }
    } catch (error) {
        console.error('Error removing actor from movie:', error);
        throw error;
    }
};

// KLUCZOWA ZMIANA: używamy endpointu z MovieDetails który zwraca role
export const getMovieActors = async (movieId: number): Promise<MovieActor[]> => {
    try {
        // Używamy tego samego endpointu co w MovieDetails z include_roles=true
        const url = `http://localhost:5000/api/movies/${movieId}?include_roles=true&_t=${Date.now()}`;

        const response = await fetch(url, {
            headers: getHeaders()
        });

        if (!response.ok) {
            throw new Error('Nie udało się pobrać aktorów filmu');
        }

        const data = await response.json();
        // Zwracamy aktorów z rolami z głównego endpointu filmu
        return data.actors || [];
    } catch (error) {
        console.error('Error fetching movie actors:', error);
        throw error;
    }
};

// ALTERNATYWNIE: jeśli chcesz używać dedykowanego endpointu cast
export const getMovieActorsFromCast = async (movieId: number): Promise<MovieActor[]> => {
    try {
        const url = `http://localhost:5000/api/movies/${movieId}/cast?_t=${Date.now()}`;

        const response = await fetch(url, {
            headers: getHeaders()
        });

        if (!response.ok) {
            throw new Error('Nie udało się pobrać obsady filmu');
        }

        const data = await response.json();
        return data || [];
    } catch (error) {
        console.error('Error fetching movie cast:', error);
        throw error;
    }
};

// REŻYSERZY
export const addDirectorToMovie = async (movieId: number, directorId: number): Promise<void> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`http://localhost:5000/api/movie-relations/movies/${movieId}/directors`, {
            method: 'POST',
            headers: getHeaders(true),
            body: JSON.stringify({ director_id: directorId })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się dodać reżysera do filmu');
        }
    } catch (error) {
        console.error('Error adding director to movie:', error);
        throw error;
    }
};

export const removeDirectorFromMovie = async (movieId: number, directorId: number): Promise<void> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`http://localhost:5000/api/movie-relations/movies/${movieId}/directors/${directorId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się usunąć reżysera z filmu');
        }
    } catch (error) {
        console.error('Error removing director from movie:', error);
        throw error;
    }
};

export const getMovieDirectors = async (movieId: number): Promise<MovieDirector[]> => {
    try {
        const url = `http://localhost:5000/api/movies/${movieId}?_t=${Date.now()}`;

        const response = await fetch(url, {
            headers: getHeaders()
        });

        if (!response.ok) {
            throw new Error('Nie udało się pobrać reżyserów filmu');
        }

        const data = await response.json();
        // Zwracamy reżyserów z głównego endpointu filmu
        return data.directors || [];
    } catch (error) {
        console.error('Error fetching movie directors:', error);
        throw error;
    }
};

// GATUNKI
export const addGenreToMovie = async (movieId: number, genreId: number): Promise<void> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`http://localhost:5000/api/movie-relations/movies/${movieId}/genres`, {
            method: 'POST',
            headers: getHeaders(true),
            body: JSON.stringify({ genre_id: genreId })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się dodać gatunku do filmu');
        }
    } catch (error) {
        console.error('Error adding genre to movie:', error);
        throw error;
    }
};

export const removeGenreFromMovie = async (movieId: number, genreId: number): Promise<void> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`http://localhost:5000/api/movie-relations/movies/${movieId}/genres/${genreId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się usunąć gatunku z filmu');
        }
    } catch (error) {
        console.error('Error removing genre from movie:', error);
        throw error;
    }
};

export const getMovieGenres = async (movieId: number): Promise<MovieGenre[]> => {
    try {
        const url = `http://localhost:5000/api/movie-relations/movies/${movieId}/genres?_t=${Date.now()}`;

        const response = await fetch(url, {
            headers: getHeaders()
        });

        if (!response.ok) {
            throw new Error('Nie udało się pobrać gatunków filmu');
        }

        const data = await response.json();
        return data.genres || [];
    } catch (error) {
        console.error('Error fetching movie genres:', error);
        throw error;
    }
};


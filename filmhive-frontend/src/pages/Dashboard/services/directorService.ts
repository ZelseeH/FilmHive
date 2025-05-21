import axios from 'axios';

const API_URL = 'http://localhost:5000/api/directors';

export interface Director {
    id: number;
    name: string;
    birth_date: string | null;
    birth_place: string;
    biography: string;
    photo_url: string | null;
    gender: 'M' | 'K' | null;
    movies?: { id: number; title: string }[];
}

interface PaginationData {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
}

interface DirectorsResponse {
    directors: Director[];
    pagination: PaginationData;
}

interface DirectorMoviesResponse {
    movies: any[];
    pagination: PaginationData;
}

const getAuthToken = (): string | null => {
    return localStorage.getItem('accessToken');
};

export const getDirectors = async (
    filter: string = '',
    page: number = 1,
    perPage: number = 10
): Promise<DirectorsResponse> => {
    try {
        const response = await fetch(
            `${API_URL}?name=${filter}&page=${page}&per_page=${perPage}`
        );

        if (!response.ok) {
            throw new Error('Nie udało się pobrać reżyserów');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching directors:', error);
        throw error;
    }
};

export const getDirectorById = async (id: number): Promise<Director> => {
    try {
        const response = await fetch(`${API_URL}/${id}`);

        if (!response.ok) {
            throw new Error('Nie udało się pobrać danych reżysera');
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching director with id ${id}:`, error);
        throw error;
    }
};

export const searchDirectors = async (
    query: string,
    page: number = 1,
    perPage: number = 10
): Promise<DirectorsResponse> => {
    try {
        const response = await fetch(
            `${API_URL}/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`
        );

        if (!response.ok) {
            throw new Error('Nie udało się wyszukać reżyserów');
        }

        return await response.json();
    } catch (error) {
        console.error('Error searching directors:', error);
        throw error;
    }
};

export const createDirector = async (directorData: FormData): Promise<Director> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`${API_URL}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: directorData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się utworzyć reżysera');
        }

        const data = await response.json();
        return data.director;
    } catch (error) {
        console.error('Error creating director:', error);
        throw error;
    }
};

export const updateDirector = async (directorId: number, directorData: FormData): Promise<Director> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`${API_URL}/${directorId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: directorData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się zaktualizować reżysera');
        }

        const data = await response.json();
        return data.director;
    } catch (error) {
        console.error(`Error updating director ${directorId}:`, error);
        throw error;
    }
};

export const uploadDirectorPhoto = async (directorId: number, photoFile: File): Promise<Director> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const formData = new FormData();
        formData.append('photo', photoFile);

        const response = await fetch(`${API_URL}/${directorId}/photo`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się przesłać zdjęcia reżysera');
        }

        const data = await response.json();
        return data.director;
    } catch (error) {
        console.error(`Error uploading photo for director ${directorId}:`, error);
        throw error;
    }
};

export const deleteDirector = async (directorId: number): Promise<void> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`${API_URL}/${directorId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się usunąć reżysera');
        }
    } catch (error) {
        console.error(`Error deleting director ${directorId}:`, error);
        throw error;
    }
};

export const getDirectorMovies = async (
    directorId: number,
    page: number = 1,
    perPage: number = 10
): Promise<DirectorMoviesResponse> => {
    try {
        const response = await fetch(
            `${API_URL}/${directorId}/movies?page=${page}&per_page=${perPage}`
        );

        if (!response.ok) {
            throw new Error('Nie udało się pobrać filmów reżysera');
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching movies for director ${directorId}:`, error);
        throw error;
    }
};

export const directorService = {
    getDirectors,
    getDirectorById,
    searchDirectors,
    createDirector,
    updateDirector,
    uploadDirectorPhoto,
    deleteDirector,
    getDirectorMovies
};

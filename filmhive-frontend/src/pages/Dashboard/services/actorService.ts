export interface Actor {
    id: number;
    name: string;
    birth_date?: string;
    birth_place?: string;
    biography?: string;
    photo_url?: string;
    gender?: 'M' | 'K' | null;
    movies?: { id: number; title: string }[];
}
export interface MovieActor {
    id: number;
    name: string;
    photo_url?: string;
    role?: string; // Rola w konkretnym filmie
}
interface ActorsResponse {
    actors: Actor[];
    pagination: {
        currentPage: number;
        totalPages: number;
        totalItems: number;
    };
}

const API_URL = 'http://localhost:5000/api/actors';

const getAuthToken = (): string | null => {
    return localStorage.getItem('accessToken');
};

export const getActors = async (
    filter: string = '',
    page: number = 1,
    perPage: number = 10
): Promise<ActorsResponse> => {
    try {
        const response = await fetch(
            `${API_URL}?name=${filter}&page=${page}&per_page=${perPage}`
        );

        if (!response.ok) {
            throw new Error('Nie udało się pobrać aktorów');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching actors:', error);
        throw error;
    }
};

export const getActorById = async (id: number): Promise<Actor> => {
    try {
        const response = await fetch(`${API_URL}/${id}`);

        if (!response.ok) {
            throw new Error('Nie udało się pobrać danych aktora');
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching actor with id ${id}:`, error);
        throw error;
    }
};

// Funkcja do tworzenia aktora
export const createActor = async (actorData: FormData): Promise<Actor> => {
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
            body: actorData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się utworzyć aktora');
        }

        return await response.json();
    } catch (error) {
        console.error('Error creating actor:', error);
        throw error;
    }
};

// Funkcja do aktualizacji aktora
export const updateActor = async (actorId: number, actorData: FormData): Promise<Actor> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`${API_URL}/${actorId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: actorData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się zaktualizować aktora');
        }

        return await response.json();
    } catch (error) {
        console.error(`Error updating actor ${actorId}:`, error);
        throw error;
    }
};

// Funkcja do usuwania aktora
export const deleteActor = async (actorId: number): Promise<void> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const response = await fetch(`${API_URL}/${actorId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się usunąć aktora');
        }
    } catch (error) {
        console.error(`Error deleting actor ${actorId}:`, error);
        throw error;
    }
};
// Funkcja do przesyłania zdjęcia aktora
export const uploadActorPhoto = async (actorId: number, photoFile: File): Promise<Actor> => {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Brak tokenu autoryzacyjnego');
    }

    try {
        const formData = new FormData();
        formData.append('photo', photoFile);

        const response = await fetch(`${API_URL}/${actorId}/photo`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się przesłać zdjęcia aktora');
        }

        return await response.json();
    } catch (error) {
        console.error(`Error uploading photo for actor ${actorId}:`, error);
        throw error;
    }
};

// src/services/actorService.ts
// services/actorService.ts
export interface Actor {
    id: number;
    name: string;
    birth_date?: string;
    birth_place?: string;
    biography?: string;
    photo_url?: string;
    movies?: { id: number; title: string }[];
}


interface ActorsResponse {
    actors: Actor[];
    pagination: {
        currentPage: number;
        totalPages: number;
        totalItems: number;
    };
}

export const getActors = async (
    filter: string = '',
    page: number = 1,
    perPage: number = 10
): Promise<ActorsResponse> => {
    try {
        const response = await fetch(
            `http://localhost:5000/api/actors?name=${filter}&page=${page}&per_page=${perPage}`
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
        const response = await fetch(`http://localhost:5000/api/actors/${id}`);

        if (!response.ok) {
            throw new Error('Nie udało się pobrać danych aktora');
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching actor with id ${id}:`, error);
        throw error;
    }
};

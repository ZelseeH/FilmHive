import { fetchWithAuth } from '../../../services/api';

export interface Actor {
    actor_id: number;
    actor_name: string;
    birth_date?: string;
    birth_place?: string;
    biography?: string;
    photo_url?: string;
    movies?: { movie_id: number; title: string }[];
}

interface ActorsResponse {
    actors: Actor[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}

export const getActors = async (
    filter: string = '',
    page: number = 1,
    perPage: number = 10
): Promise<ActorsResponse> => {
    try {
        const response = await fetchWithAuth(
            `actors?name=${encodeURIComponent(filter)}&page=${page}&per_page=${perPage}`
        );

        return response;
    } catch (error) {
        console.error('Error fetching actors:', error);
        throw error;
    }
};

export const getActorById = async (actor_id: number): Promise<Actor> => {
    try {
        const response = await fetchWithAuth(`actors/${actor_id}`);
        return response;
    } catch (error) {
        console.error(`Error fetching actor with id ${actor_id}:`, error);
        throw error;
    }
};

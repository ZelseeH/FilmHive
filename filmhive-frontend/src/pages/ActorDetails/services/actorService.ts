import { fetchWithAuth } from '../../../services/api';

export interface Actor {
    id: number;
    name: string;
    birth_date: string | null;
    birth_place: string;
    biography: string;
    photo_url: string | null;
    gender: 'M' | 'K' | null;
}

export interface ActorMovie {
    id: number;
    title: string;
    release_date: string;
    poster_url: string;
    actor_role: string;
    duration_minutes: number;
    average_rating: number | null;
}

export const getActorById = async (actorId: number): Promise<Actor> => {
    return fetchWithAuth(`actors/${actorId}`);
};

export const getAllActors = async (page = 1, perPage = 10): Promise<{
    actors: Actor[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}> => {
    return fetchWithAuth(`actors?page=${page}&per_page=${perPage}`);
};

export const searchActors = async (query: string, page = 1, perPage = 10): Promise<{
    actors: Actor[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}> => {
    return fetchWithAuth(`actors/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`);
};

export const filterActors = async (
    filters: {
        name?: string;
        birth_place?: string;
        gender?: 'M' | 'K';
    },
    page = 1,
    perPage = 10,
    sortBy = 'name',
    sortOrder = 'asc'
): Promise<{
    actors: Actor[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
    sort_by: string;
    sort_order: string;
}> => {
    const queryParams = new URLSearchParams();

    queryParams.append('page', page.toString());
    queryParams.append('per_page', perPage.toString());
    queryParams.append('sort_by', sortBy);
    queryParams.append('sort_order', sortOrder);

    if (filters.name) queryParams.append('name', filters.name);
    if (filters.birth_place) queryParams.append('countries', filters.birth_place);
    if (filters.gender) queryParams.append('gender', filters.gender);

    return fetchWithAuth(`actors/filter?${queryParams.toString()}`);
};

export const getBirthplaces = async (): Promise<{
    birthplaces: string[];
}> => {
    return fetchWithAuth('actors/birthplaces');
};

export const getActorMovies = async (
    actorId: number,
    page = 1,
    perPage = 10,
    sortField = 'release_date',
    sortOrder = 'asc'
): Promise<{
    movies: ActorMovie[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
    sort_field: string;
    sort_order: string;
}> => {
    const url = `actors/${actorId}/movies?page=${page}&per_page=${perPage}&sort_field=${sortField}&sort_order=${sortOrder}`;
    return fetchWithAuth(url);
};

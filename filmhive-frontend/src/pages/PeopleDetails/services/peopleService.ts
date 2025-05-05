import { fetchWithAuth } from '../../../services/api';

export interface Person {
    id: number;
    name: string;
    birth_date: string | null;
    birth_place: string;
    biography: string;
    photo_url: string | null;
    gender: 'M' | 'K' | null;
    type: 'actor' | 'director';
}

export interface PersonMovie {
    id: number;
    title: string;
    release_date: string;
    poster_url: string;
    actor_role?: string; // Opcjonalne, tylko dla aktorów
    duration_minutes: number;
    average_rating: number | null;
}

export const getPersonById = async (personId: number, type: 'actor' | 'director'): Promise<Person> => {
    return fetchWithAuth(`people/${type}/${personId}`);
};

export const getAllPeople = async (page = 1, perPage = 10, type?: 'actor' | 'director'): Promise<{
    people: Person[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}> => {
    const queryParams = new URLSearchParams();
    queryParams.append('page', page.toString());
    queryParams.append('per_page', perPage.toString());

    if (type) {
        queryParams.append('type', type);
    }

    return fetchWithAuth(`people?${queryParams.toString()}`);
};

export const searchPeople = async (query: string, page = 1, perPage = 10, type?: 'actor' | 'director'): Promise<{
    people: Person[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}> => {
    const queryParams = new URLSearchParams();
    queryParams.append('q', query);
    queryParams.append('page', page.toString());
    queryParams.append('per_page', perPage.toString());

    if (type) {
        queryParams.append('type', type);
    }

    return fetchWithAuth(`people/search?${queryParams.toString()}`);
};

export const filterPeople = async (
    filters: {
        name?: string;
        countries?: string;
        years?: string;
        gender?: 'M' | 'K';
        type?: 'actor' | 'director';
    },
    page = 1,
    perPage = 10,
    sortBy = 'name',
    sortOrder = 'asc'
): Promise<{
    people: Person[];
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
    if (filters.countries) queryParams.append('countries', filters.countries);
    if (filters.years) queryParams.append('years', filters.years);
    if (filters.gender) queryParams.append('gender', filters.gender);
    if (filters.type) queryParams.append('type', filters.type);

    return fetchWithAuth(`people/filter?${queryParams.toString()}`);
};

export const getBirthplaces = async (): Promise<{
    birthplaces: string[];
}> => {
    return fetchWithAuth('people/birthplaces');
};

export const getPersonMovies = async (personId: number, type: 'actor' | 'director', page = 1, perPage = 10): Promise<{
    movies: PersonMovie[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}> => {
    return fetchWithAuth(`people/${type}/${personId}/movies?page=${page}&per_page=${perPage}`);
};

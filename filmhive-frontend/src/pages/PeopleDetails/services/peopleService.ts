import { fetchWithAuth } from '../../../services/api';

export interface Person {
    id: number;
    name: string;
    birth_date?: string | null;
    birth_place?: string;
    biography?: string;
    photo_url?: string | null;
    gender?: 'M' | 'K' | null;
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
    try {
        const data = await fetchWithAuth(`people/${type}/${personId}`);
        return data;
    } catch (error) {
        console.error(`Error fetching person with id ${personId}:`, error);
        throw error;
    }
};

export const getAllPeople = async (
    page = 1,
    perPage = 10,
    type?: 'actor' | 'director'
): Promise<{
    people: Person[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}> => {
    try {
        const queryParams = new URLSearchParams();
        queryParams.append('page', page.toString());
        queryParams.append('per_page', perPage.toString());

        if (type) {
            queryParams.append('type', type);
        }

        const data = await fetchWithAuth(`people?${queryParams.toString()}`);
        return data;
    } catch (error) {
        console.error('Error fetching all people:', error);
        throw error;
    }
};

export const searchPeople = async (
    query: string,
    page = 1,
    perPage = 10,
    type?: 'actor' | 'director'
): Promise<{
    people: Person[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}> => {
    try {
        const queryParams = new URLSearchParams();
        queryParams.append('q', query);
        queryParams.append('page', page.toString());
        queryParams.append('per_page', perPage.toString());

        if (type) {
            queryParams.append('type', type);
        }

        const data = await fetchWithAuth(`people/search?${queryParams.toString()}`);
        return data;
    } catch (error) {
        console.error('Error searching people:', error);
        throw error;
    }
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
    try {
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

        const data = await fetchWithAuth(`people/filter?${queryParams.toString()}`);
        return data;
    } catch (error) {
        console.error('Error filtering people:', error);
        throw error;
    }
};

export const getBirthplaces = async (): Promise<{
    birthplaces: string[];
}> => {
    try {
        const data = await fetchWithAuth('people/birthplaces');
        return data;
    } catch (error) {
        console.error('Error fetching birthplaces:', error);
        throw error;
    }
};

// ✨ POPRAWIONA METODA - z sortowaniem
export const getPersonMovies = async (
    personId: number,
    type: 'actor' | 'director',
    page = 1,
    perPage: number | 'all' = 20,
    sortField = 'release_date',  // NOWY parametr
    sortOrder = 'desc'           // NOWY parametr
): Promise<{
    movies: PersonMovie[];
    pagination: {
        page: number;
        per_page: number | null;
        total: number;
        total_pages: number;
    };
    sort_field: string;          // NOWY w odpowiedzi
    sort_order: string;          // NOWY w odpowiedzi
}> => {
    try {
        const queryParams = new URLSearchParams();
        queryParams.append('page', page.toString());

        if (perPage === 'all') {
            queryParams.append('per_page', 'all');
        } else {
            queryParams.append('per_page', perPage.toString());
        }

        // ✨ NOWE - dodaj parametry sortowania
        queryParams.append('sort_field', sortField);
        queryParams.append('sort_order', sortOrder);

        const response = await fetchWithAuth(`people/${type}/${personId}/movies?${queryParams.toString()}`);

        // Obsługa nowej struktury odpowiedzi z backend
        if (response.success) {
            return response.data;
        } else {
            throw new Error(response.error || 'Failed to fetch movies');
        }
    } catch (error) {
        console.error(`Error fetching movies for person id ${personId}:`, error);
        throw error;
    }
};

// ✨ DODATKOWE - funkcje pomocnicze dla konkretnych typów
export const getActorMovies = async (
    actorId: number,
    page = 1,
    perPage: number | 'all' = 20,
    sortField = 'release_date',
    sortOrder = 'desc'
): Promise<{
    movies: PersonMovie[];
    pagination: {
        page: number;
        per_page: number | null;
        total: number;
        total_pages: number;
    };
}> => {
    return getPersonMovies(actorId, 'actor', page, perPage, sortField, sortOrder);
};

export const getDirectorMovies = async (
    directorId: number,
    page = 1,
    perPage: number | 'all' = 20,
    sortField = 'release_date',
    sortOrder = 'desc'
): Promise<{
    movies: PersonMovie[];
    pagination: {
        page: number;
        per_page: number | null;
        total: number;
        total_pages: number;
    };
}> => {
    return getPersonMovies(directorId, 'director', page, perPage, sortField, sortOrder);
};

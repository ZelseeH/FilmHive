const API_URL = 'http://localhost:5000/api/people';
export interface Person {
    id: number;
    name: string;
    birth_date?: string;
    birth_place?: string;
    biography?: string;
    photo_url?: string;
    gender?: string;
    type: 'actor' | 'director';
    movies?: { id: number; title: string }[];
}

interface PeopleResponse {
    data: Person[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}

export const getPeople = async (
    type: 'actor' | 'director' = 'actor',
    filter: string = '',
    page: number = 1,
    perPage: number = 10
): Promise<PeopleResponse> => {
    const params = new URLSearchParams({
        type,
        name: filter,
        page: page.toString(),
        per_page: perPage.toString(),
    });

    try {
        const response = await fetch(`${API_URL}?${params}`);
        if (!response.ok) {
            throw new Error('Nie udało się pobrać osób');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching people:', error);
        throw error;
    }
};

export const getPersonById = async (
    id: number,
    type: 'actor' | 'director' = 'actor'
): Promise<Person> => {
    try {
        const response = await fetch(`${API_URL}/${id}?type=${type}`);
        if (!response.ok) {
            throw new Error('Nie udało się pobrać danych osoby');
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching person with id ${id}:`, error);
        throw error;
    }
};

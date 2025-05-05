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
    people: Person[];
    pagination: {
        page: number;
        total_pages: number;
        total: number;
        per_page: number;
    };
}

export const getPeople = async (
    filter: string = '',
    page: number = 1,
    perPage: number = 10,
    type?: 'actor' | 'director'
): Promise<PeopleResponse> => {
    try {
        let url = `http://localhost:5000/api/people?name=${filter}&page=${page}&per_page=${perPage}`;

        if (type) {
            url += `&type=${type}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error('Nie udało się pobrać osób');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching people:', error);
        throw error;
    }
};

export const getPersonById = async (id: number, type: 'actor' | 'director'): Promise<Person> => {
    try {
        const response = await fetch(`http://localhost:5000/api/people/${type}/${id}`);

        if (!response.ok) {
            throw new Error(`Nie udało się pobrać danych osoby`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching person with id ${id}:`, error);
        throw error;
    }
};

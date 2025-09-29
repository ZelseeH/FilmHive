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

export interface PeopleResponse {
    people: Person[];
    pagination: {
        page: number;
        total_pages: number;
        total: number;
        per_page: number;
    };
}

export const getPeopleWithBirthdayToday = async (): Promise<Person[]> => {
    try {
        const response = await fetch(`http://localhost:5000/api/people/birthdays/today`);

        if (!response.ok) {
            throw new Error('Nie udało się pobrać osób z urodzinami');
        }

        const data = await response.json();

        // Zwracamy tylko listę osób (nie paginację)
        return data.birthdays_today as Person[];
    } catch (error) {
        console.error('Error fetching people with birthday today:', error);
        throw error;
    }
};

// models/People.ts

// Wspólny interfejs dla osób (aktorów i reżyserów)
export interface Person {
    id: number;
    name: string;
    birth_date?: string;
    birth_place?: string;
    biography?: string;
    photo_url?: string;
    gender?: string;
    type: 'actor' | 'director'; // Dodajemy pole type do rozróżniania
    movies?: { id: number; title: string }[];
}

// Dla zachowania kompatybilności wstecznej
export interface Actor extends Omit<Person, 'type'> {
    type: 'actor';
}

export interface Director extends Omit<Person, 'type'> {
    type: 'director';
}

// Interfejs dla odpowiedzi z API
export interface PeopleResponse {
    people: Person[];
    pagination: {
        page: number;
        total_pages: number;
        total: number;
        per_page: number;
    };
    sort_by?: string;
    sort_order?: string;
}

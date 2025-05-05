export interface Person {
    id: number;
    name: string;
    birth_date: string | null;
    birth_place: string;
    biography: string;
    photo_url: string | null;
    gender: 'M' | 'K' | null;
    type: 'actor' | 'director';
    movies?: {
        id: number;
        title: string;
    }[];
}

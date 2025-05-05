export interface Actor {
    id: number;
    name: string;
    birth_date: string | null;
    birth_place: string;
    biography: string;
    photo_url: string | null;
    gender: 'M' | 'K' | null;
    movies?: {
        id: number;
        title: string;
    }[];
}

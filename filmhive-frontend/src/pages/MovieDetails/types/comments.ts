export interface Comment {
    id: number;
    user_id: number;
    movie_id: number;
    text: string;
    created_at: string;
    user_rating?: number | null; // DODANE - ocena użytkownika
    user?: {
        user_id: number;
        username: string;
        profile_picture?: string | null; // DODANE - avatar
    };
}

export interface PaginationData {
    page: number;
    total_pages: number;
    total: number;
    per_page: number;
}

export interface CommentsResponse {
    comments: Comment[];
    pagination: PaginationData;
}

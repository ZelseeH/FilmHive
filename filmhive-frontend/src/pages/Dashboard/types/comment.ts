export interface Comment {
    id: number;
    user_id: number;
    movie_id: number;
    text: string;
    created_at: string;
    user?: {
        id: number;
        username: string;
        profile_picture?: string;
    };
    movie?: {
        id: number;
        title: string;
    };
    user_rating?: {
        rating: number;
        rated_at: string;
    } | null;
}

export interface CommentsPagination {
    total: number;
    total_pages: number;
    page: number;
    per_page: number;
}

export interface CommentsResponse {
    comments: Comment[];
    pagination: CommentsPagination;
    filters?: {
        search?: string;
        date_from?: string;
        date_to?: string;
        sort_by: string;
        sort_order: string;
    };
}

export interface CommentFilters {
    page?: number;
    per_page?: number;
    search?: string;
    date_from?: string;
    date_to?: string;
    sort_by?: 'created_at' | 'movie_title' | 'username';
    sort_order?: 'asc' | 'desc';
    include_ratings?: boolean;
}

export interface CommentsStatistics {
    total_comments: number;
    recent_comments_24h: number;
    weekly_comments: number;
    most_active_user?: {
        user_id: number;
        username: string;
        comment_count: number;
    } | null;
}

export interface ApiError {
    error: string;
    message?: string;
}

export interface Reply {
    id: number;                    // ZMIEŃ z reply_id na id (backend zwraca "id")
    comment_id: number;
    reply_user_id: number;
    main_user_id: number;
    text: string;
    created_at: string;
    user_rating?: number | null;
    reply_user: {
        user_id: number;
        username: string;
        profile_picture?: string | null;
    };
    main_user: {
        user_id: number;
        username: string;
        profile_picture?: string | null;
    };
}

export interface ThreadData {
    main_comment: {
        id: number;                // ZMIEŃ z comment_id na id (backend zwraca "id")
        user_id: number;
        movie_id: number;
        comment_text: string;
        created_at: string;
        user_rating?: number | null;
        user: {
            user_id: number;
            username: string;
            profile_picture?: string | null;
        };
    };
    replies: Reply[];
    replies_count: number;
}

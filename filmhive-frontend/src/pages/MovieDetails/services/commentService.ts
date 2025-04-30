import { fetchWithAuth } from '../../../services/api';

export interface Comment {
    comment_id: number;
    user_id: number;
    movie_id: number;
    text: string;
    created_at: string;
    user_rating?: number;
    user?: {
        user_id: number;
        username: string;
        profile_picture?: string;
    };
}

export interface CommentResponse {
    comments: Comment[];
    pagination: {
        total: number;
        total_pages: number;
        page: number;
        per_page: number;
    };
}

export class CommentService {
    static async getMovieComments(movieId: number, page: number = 1, perPage: number = 10): Promise<CommentResponse> {
        return fetchWithAuth(`comments/movie/${movieId}?page=${page}&per_page=${perPage}`);
    }

    static async getMovieCommentsWithRatings(
        movieId: number,
        page: number = 1,
        perPage: number = 10,
        sortBy: string = 'created_at',
        sortOrder: string = 'desc'
    ): Promise<CommentResponse> {
        return fetchWithAuth(
            `comments/movie/${movieId}/with-ratings?page=${page}&per_page=${perPage}&sort_by=${sortBy}&sort_order=${sortOrder}`
        );
    }

    static async addComment(movieId: number, commentText: string): Promise<Comment> {
        return fetchWithAuth(`comments/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ movie_id: movieId, comment_text: commentText })
        });
    }

    static async updateComment(commentId: number, commentText: string): Promise<Comment> {
        return fetchWithAuth(`comments/update/${commentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ comment_text: commentText })
        });
    }

    static async deleteComment(commentId: number): Promise<void> {
        await fetchWithAuth(`comments/delete/${commentId}`, {
            method: 'DELETE'
        });
    }

    static async getCommentCount(movieId: number): Promise<number> {
        const data = await fetchWithAuth(`comments/count/${movieId}`);
        return data.count ?? 0;
    }

    static async getUserComments(page: number = 1, perPage: number = 10): Promise<CommentResponse> {
        return fetchWithAuth(`comments/user?page=${page}&per_page=${perPage}`);
    }

<<<<<<< Updated upstream
    static async getUserComment(movieId: number, token: string): Promise<Comment | null> {
        const response = await fetch(`http://localhost:5000/api/comments/user/${movieId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (response.status === 404) {
            return null;
        }

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się pobrać komentarza użytkownika: ${response.status}`);
        }

        return await response.json();
=======
    static async getUserComment(movieId: number): Promise<Comment | null> {
        try {
            const response = await fetchWithAuth(`comments/user/${movieId}`);
            return response ?? null;
        } catch (error) {
            console.warn('Błąd podczas pobierania komentarza użytkownika:', error);
            return null;
        }
>>>>>>> Stashed changes
    }
}

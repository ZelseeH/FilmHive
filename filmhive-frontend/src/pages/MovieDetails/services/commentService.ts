export interface Comment {
    id: number;
    user_id: number;
    movie_id: number;
    text: string;
    created_at: string;
    user?: {
        id: number;
        username: string;
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
        const response = await fetch(`http://localhost:5000/api/comments/movie/${movieId}?page=${page}&per_page=${perPage}`, {
            headers: {
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się pobrać komentarzy: ${response.status}`);
        }

        return await response.json();
    }

    static async addComment(movieId: number, commentText: string, token: string): Promise<Comment> {
        const response = await fetch(`http://localhost:5000/api/comments/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ movie_id: movieId, comment_text: commentText })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się dodać komentarza: ${response.status}`);
        }

        return await response.json();
    }

    static async updateComment(commentId: number, commentText: string, token: string): Promise<Comment> {
        const response = await fetch(`http://localhost:5000/api/comments/update/${commentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ comment_text: commentText })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się zaktualizować komentarza: ${response.status}`);
        }

        return await response.json();
    }

    static async deleteComment(commentId: number, token: string): Promise<void> {
        const response = await fetch(`http://localhost:5000/api/comments/delete/${commentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się usunąć komentarza: ${response.status}`);
        }
    }

    static async getCommentCount(movieId: number): Promise<number> {
        const response = await fetch(`http://localhost:5000/api/comments/count/${movieId}`);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się pobrać liczby komentarzy: ${response.status}`);
        }

        const data = await response.json();
        return data.count ?? 0;
    }

    static async getUserComments(token: string, page: number = 1, perPage: number = 10): Promise<CommentResponse> {
        const response = await fetch(`http://localhost:5000/api/comments/user?page=${page}&per_page=${perPage}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się pobrać komentarzy użytkownika: ${response.status}`);
        }

        return await response.json();
    }


    static async getUserComment(movieId: number, token: string): Promise<Comment | null> {
        const response = await fetch(`http://localhost:5000/api/comments/user/${movieId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (response.status === 404) {
            return null; // Użytkownik nie ma jeszcze komentarza
        }

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się pobrać komentarza użytkownika: ${response.status}`);
        }

        return await response.json();
    }


}

import { Comment, CommentsResponse, CommentFilters, CommentsStatistics } from '../types/comment';

const API_BASE_URL = 'http://localhost:5000/api';

// Funkcja do pobierania tokenu (tak jak w directorService)
const getAuthToken = (): string | null => {
    return localStorage.getItem('accessToken'); // Zmienione z 'access_token' na 'accessToken'
};

export const commentService = {
    // STAFF ENDPOINTS

    /**
     * Pobiera wszystkie komentarze w systemie (tylko dla staff)
     */
    getAllComments: async (params: CommentFilters = {}): Promise<CommentsResponse> => {
        try {
            const queryParams = new URLSearchParams();

            if (params.page) queryParams.append('page', params.page.toString());
            if (params.per_page) queryParams.append('per_page', params.per_page.toString());
            if (params.search) queryParams.append('search', params.search);
            if (params.date_from) queryParams.append('date_from', params.date_from);
            if (params.date_to) queryParams.append('date_to', params.date_to);
            if (params.sort_by) queryParams.append('sort_by', params.sort_by);
            if (params.sort_order) queryParams.append('sort_order', params.sort_order);

            const response = await fetch(`${API_BASE_URL}/comments/all?${queryParams}`);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Nie udało się pobrać komentarzy');
            }

            return await response.json();
        } catch (error: any) {
            console.error('Error fetching all comments:', error);
            throw new Error(error.message || 'Nie udało się pobrać komentarzy');
        }
    },

    /**
     * Aktualizuje komentarz przez staff
     */
    updateCommentByStaff: async (commentId: number, commentText: string): Promise<Comment> => {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/comments/staff/update/${commentId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    comment_text: commentText
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Nie udało się zaktualizować komentarza');
            }

            return await response.json();
        } catch (error: any) {
            console.error('Error updating comment by staff:', error);
            throw new Error(error.message || 'Nie udało się zaktualizować komentarza');
        }
    },

    /**
     * Usuwa komentarz przez staff
     */
    deleteCommentByStaff: async (commentId: number): Promise<{ message: string }> => {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/comments/staff/delete/${commentId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Nie udało się usunąć komentarza');
            }

            return await response.json();
        } catch (error: any) {
            console.error('Error deleting comment by staff:', error);
            throw new Error(error.message || 'Nie udało się usunąć komentarza');
        }
    },

    /**
     * Pobiera szczegółowe informacje o komentarzu
     */
    getCommentDetails: async (commentId: number): Promise<Comment> => {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/comments/staff/details/${commentId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Nie udało się pobrać szczegółów komentarza');
            }

            return await response.json();
        } catch (error: any) {
            console.error('Error fetching comment details:', error);
            throw new Error(error.message || 'Nie udało się pobrać szczegółów komentarza');
        }
    },

    /**
     * Pobiera statystyki komentarzy
     */
    getCommentsStatistics: async (): Promise<CommentsStatistics> => {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/comments/staff/statistics`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Nie udało się pobrać statystyk');
            }

            return await response.json();
        } catch (error: any) {
            console.error('Error fetching comments statistics:', error);
            throw new Error(error.message || 'Nie udało się pobrać statystyk');
        }
    },

    // USER ENDPOINTS (dla zwykłych użytkowników)

    /**
     * Pobiera komentarze dla filmu
     */
    getMovieComments: async (movieId: number, params: CommentFilters = {}): Promise<CommentsResponse> => {
        try {
            const queryParams = new URLSearchParams();
            if (params.page) queryParams.append('page', params.page.toString());
            if (params.per_page) queryParams.append('per_page', params.per_page.toString());
            if (params.sort_by) queryParams.append('sort_by', params.sort_by);
            if (params.sort_order) queryParams.append('sort_order', params.sort_order);
            if (params.include_ratings !== undefined) queryParams.append('include_ratings', params.include_ratings.toString());

            const response = await fetch(`${API_BASE_URL}/comments/movie/${movieId}?${queryParams}`);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Nie udało się pobrać komentarzy filmu');
            }

            return await response.json();
        } catch (error: any) {
            console.error('Error fetching movie comments:', error);
            throw new Error(error.message || 'Nie udało się pobrać komentarzy filmu');
        }
    },

    /**
     * Dodaje nowy komentarz
     */
    addComment: async (movieId: number, commentText: string): Promise<Comment> => {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/comments/add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    movie_id: movieId,
                    comment_text: commentText
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Nie udało się dodać komentarza');
            }

            return await response.json();
        } catch (error: any) {
            console.error('Error adding comment:', error);
            throw new Error(error.message || 'Nie udało się dodać komentarza');
        }
    },

    /**
     * Aktualizuje komentarz użytkownika
     */
    updateComment: async (commentId: number, commentText: string): Promise<Comment> => {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/comments/update/${commentId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    comment_text: commentText
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Nie udało się zaktualizować komentarza');
            }

            return await response.json();
        } catch (error: any) {
            console.error('Error updating comment:', error);
            throw new Error(error.message || 'Nie udało się zaktualizować komentarza');
        }
    },

    /**
     * Usuwa komentarz użytkownika
     */
    deleteComment: async (commentId: number): Promise<{ message: string }> => {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/comments/delete/${commentId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Nie udało się usunąć komentarza');
            }

            return await response.json();
        } catch (error: any) {
            console.error('Error deleting comment:', error);
            throw new Error(error.message || 'Nie udało się usunąć komentarza');
        }
    }
};

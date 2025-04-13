import { useState, useEffect, useRef, useCallback } from 'react';
import { CommentService } from '../services/commentService';
import { User } from '../../../contexts/AuthContext';

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

interface UseCommentsProps {
    movieId: number;
    user: User | null;
    getToken: () => string | null;
}

export const useComments = ({ movieId, user, getToken }: UseCommentsProps) => {
    const [comments, setComments] = useState<Comment[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [pagination, setPagination] = useState({
        total: 0,
        total_pages: 0,
        page: 1,
        per_page: 10
    });
    const fetchingRef = useRef<boolean>(false);
    const getUserComment = useCallback(async () => {
        if (!user) return null;
        setIsLoading(true);
        setError(null);
        try {
            const token = getToken();
            if (!token) throw new Error('Brak tokenu autoryzacyjnego');
            const comment = await CommentService.getUserComment(movieId, token);
            return comment;
        } catch (err) {
            console.error('Błąd podczas pobierania komentarza użytkownika:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [user, movieId, getToken]);

    const fetchComments = useCallback(async (page: number = 1) => {
        if (!movieId || fetchingRef.current) return;

        fetchingRef.current = true;
        setIsLoading(true);
        setError(null);

        try {
            const result = await CommentService.getMovieComments(movieId, page);
            setComments(result.comments);
            setPagination(result.pagination);
        } catch (error) {
            console.error('Błąd podczas pobierania komentarzy:', error);
            setError('Nie udało się pobrać komentarzy');
        } finally {
            setIsLoading(false);
            fetchingRef.current = false;
        }
    }, [movieId]);

    useEffect(() => {
        fetchComments(1);

        return () => {
            fetchingRef.current = false;
        };
    }, [movieId, fetchComments]);

    const addComment = async (commentText: string) => {
        if (!user || isLoading || !movieId) return null;

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return null;
            }

            const newComment = await CommentService.addComment(movieId, commentText, token);

            await fetchComments(pagination.page);

            return newComment;
        } catch (error) {
            console.error('Błąd podczas dodawania komentarza:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    const updateComment = async (commentId: number, commentText: string) => {
        if (!user || isLoading) return null;

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return null;
            }

            const updatedComment = await CommentService.updateComment(commentId, commentText, token);

            // Aktualizacja komentarza w lokalnym stanie
            setComments(prevComments =>
                prevComments.map(comment =>
                    comment.id === commentId ? updatedComment : comment
                )
            );

            return updatedComment;
        } catch (error) {
            console.error('Błąd podczas aktualizacji komentarza:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    const deleteComment = async (commentId: number) => {
        if (!user || isLoading) return false;

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return false;
            }

            await CommentService.deleteComment(commentId, token);
            setComments(prevComments =>
                prevComments.filter(comment => comment.id !== commentId)
            );
            setPagination(prev => ({
                ...prev,
                total: Math.max(0, prev.total - 1)
            }));

            return true;
        } catch (error) {
            console.error('Błąd podczas usuwania komentarza:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    const changePage = (page: number) => {
        if (page < 1 || page > pagination.total_pages || isLoading) return;
        fetchComments(page);
    };

    return {
        comments,
        isLoading,
        error,
        pagination,
        addComment,
        updateComment,
        deleteComment,
        changePage,
        getUserComment,
        refreshComments: fetchComments
    };
};

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
        console.log('[useComments] getUserComment called', { movieId, user });
        if (!user) {
            console.log('[useComments] getUserComment: brak użytkownika');
            return null;
        }
        setIsLoading(true);
        setError(null);
        try {
            const token = getToken();
            if (!token) throw new Error('Brak tokenu autoryzacyjnego');
            const comment = await CommentService.getUserComment(movieId, token);
            console.log('[useComments] getUserComment: pobrano komentarz', comment);
            return comment;
        } catch (err) {
            console.error('[useComments] Błąd podczas pobierania komentarza użytkownika:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [user, movieId, getToken]);

    const fetchComments = useCallback(async (page: number = 1) => {
        console.log('[useComments] fetchComments called', { movieId, page });
        if (!movieId || fetchingRef.current) {
            console.log('[useComments] fetchComments: brak movieId lub już trwa pobieranie');
            return;
        }

        fetchingRef.current = true;
        setIsLoading(true);
        setError(null);

        try {
            const result = await CommentService.getMovieComments(movieId, page);
            console.log('[useComments] fetchComments: pobrano komentarze', result);
            setComments(result.comments);
            setPagination(result.pagination);
        } catch (error) {
            console.error('[useComments] Błąd podczas pobierania komentarzy:', error);
            setError('Nie udało się pobrać komentarzy');
        } finally {
            setIsLoading(false);
            fetchingRef.current = false;
        }
    }, [movieId]);

    useEffect(() => {
        console.log('[useComments] useEffect: movieId się zmienił', movieId);
        fetchComments(1);

        return () => {
            fetchingRef.current = false;
        };
    }, [movieId, fetchComments]);

    const addComment = async (commentText: string) => {
        console.log('[useComments] addComment called', { movieId, user, commentText });
        if (!user || isLoading || !movieId) {
            console.log('[useComments] addComment: brak user/isLoading/movieId');
            return null;
        }

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return null;
            }

            const newComment = await CommentService.addComment(movieId, commentText, token);
            console.log('[useComments] addComment: komentarz dodany', newComment);

            await fetchComments(pagination.page);

            return newComment;
        } catch (error) {
            console.error('[useComments] Błąd podczas dodawania komentarza:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    const updateComment = async (commentId: number, commentText: string) => {
        console.log('[useComments] updateComment called', { commentId, commentText });
        if (!user || isLoading) {
            console.log('[useComments] updateComment: brak user/isLoading');
            return null;
        }

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return null;
            }

            const updatedComment = await CommentService.updateComment(commentId, commentText, token);
            console.log('[useComments] updateComment: komentarz zaktualizowany', updatedComment);

            // Aktualizacja komentarza w lokalnym stanie
            setComments(prevComments =>
                prevComments.map(comment =>
                    comment.id === commentId ? updatedComment : comment
                )
            );

            return updatedComment;
        } catch (error) {
            console.error('[useComments] Błąd podczas aktualizacji komentarza:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    const deleteComment = async (commentId: number) => {
        console.log('[useComments] deleteComment called', { commentId });
        if (!user || isLoading) {
            console.log('[useComments] deleteComment: brak user/isLoading');
            return false;
        }

        setIsLoading(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return false;
            }

            await CommentService.deleteComment(commentId, token);
            console.log('[useComments] deleteComment: komentarz usunięty', commentId);
            setComments(prevComments =>
                prevComments.filter(comment => comment.id !== commentId)
            );
            setPagination(prev => ({
                ...prev,
                total: Math.max(0, prev.total - 1)
            }));

            return true;
        } catch (error) {
            console.error('[useComments] Błąd podczas usuwania komentarza:', error);
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    const changePage = (page: number) => {
        console.log('[useComments] changePage called', { page });
        if (page < 1 || page > pagination.total_pages || isLoading) {
            console.log('[useComments] changePage: nieprawidłowa strona lub ładowanie');
            return;
        }
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


import { useState, useEffect, useRef, useCallback } from 'react';
import { CommentService } from '../services/commentService';
import { User } from '../../../contexts/AuthContext';

export interface Comment {
    comment_id: number;
    user_id: number;
    movie_id: number;
    text: string;
    created_at: string;
    user?: {
        user_id: number;
        username: string;
    };
}

interface UseCommentsProps {
    movieId: number;
    user: User | null;
}

export const useComments = ({ movieId, user }: UseCommentsProps) => {
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
<<<<<<< Updated upstream
            const token = getToken();
            if (!token) throw new Error('Brak tokenu autoryzacyjnego');
            const comment = await CommentService.getUserComment(movieId, token);
            return comment;
        } catch (err) {
            console.error('Błąd podczas pobierania komentarza użytkownika:', err);
=======
            const comment = await CommentService.getUserComment(movieId);
            return comment;
        } catch (err) {
>>>>>>> Stashed changes
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [user, movieId]);

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
<<<<<<< Updated upstream
            console.error('Błąd podczas pobierania komentarzy:', error);
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
        setIsLoading(true);
        setError(null);

        try {
<<<<<<< Updated upstream
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return null;
            }

            const newComment = await CommentService.addComment(movieId, commentText, token);

=======
            const newComment = await CommentService.addComment(movieId, commentText);
>>>>>>> Stashed changes
            await fetchComments(pagination.page);

            return newComment;
        } catch (error) {
<<<<<<< Updated upstream
            console.error('Błąd podczas dodawania komentarza:', error);
=======
>>>>>>> Stashed changes
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    const updateComment = async (commentId: number, commentText: string) => {
        if (!user || isLoading) return null;
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
        setIsLoading(true);
        setError(null);

        try {
            const updatedComment = await CommentService.updateComment(commentId, commentText);

<<<<<<< Updated upstream
            const updatedComment = await CommentService.updateComment(commentId, commentText, token);

            // Aktualizacja komentarza w lokalnym stanie
=======
>>>>>>> Stashed changes
            setComments(prevComments =>
                prevComments.map(comment =>
                    comment.comment_id === commentId ? updatedComment : comment
                )
            );

            return updatedComment;
        } catch (error) {
<<<<<<< Updated upstream
            console.error('Błąd podczas aktualizacji komentarza:', error);
=======
>>>>>>> Stashed changes
            setError(error instanceof Error ? error.message : 'Wystąpił nieznany błąd');
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    const deleteComment = async (commentId: number) => {
        if (!user || isLoading) return false;
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
        setIsLoading(true);
        setError(null);

        try {
<<<<<<< Updated upstream
            const token = getToken();
            if (!token) {
                setError('Brak tokenu autoryzacyjnego');
                return false;
            }

            await CommentService.deleteComment(commentId, token);
=======
            await CommentService.deleteComment(commentId);
>>>>>>> Stashed changes
            setComments(prevComments =>
                prevComments.filter(comment => comment.comment_id !== commentId)
            );
            setPagination(prev => ({
                ...prev,
                total: Math.max(0, prev.total - 1)
            }));

            return true;
        } catch (error) {
<<<<<<< Updated upstream
            console.error('Błąd podczas usuwania komentarza:', error);
=======
>>>>>>> Stashed changes
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
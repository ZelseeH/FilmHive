import { useState, useEffect, useCallback } from 'react';
import { commentService } from '../services/commentService';
import { Comment, CommentsPagination, CommentFilters, CommentsStatistics } from '../types/comment';

interface UseCommentsReturn {
    comments: Comment[];
    loading: boolean;
    error: string | null;
    pagination: CommentsPagination;
    fetchAllComments: (params?: CommentFilters) => Promise<void>;
    updateCommentByStaff: (commentId: number, commentText: string) => Promise<Comment>;
    deleteCommentByStaff: (commentId: number) => Promise<boolean>;
    getCommentDetails: (commentId: number) => Promise<Comment>;
    setError: (error: string | null) => void;
    setComments: (comments: Comment[]) => void;
}

export const useComments = (): UseCommentsReturn => {
    const [comments, setComments] = useState<Comment[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [pagination, setPagination] = useState<CommentsPagination>({
        total: 0,
        total_pages: 0,
        page: 1,
        per_page: 20
    });

    // Pobieranie wszystkich komentarzy (dla staff)
    const fetchAllComments = useCallback(async (params: CommentFilters = {}) => {
        setLoading(true);
        setError(null);
        try {
            const data = await commentService.getAllComments(params);
            setComments(data.comments || []);
            setPagination(data.pagination || {
                total: 0,
                total_pages: 0,
                page: 1,
                per_page: 20
            });
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    // Aktualizacja komentarza przez staff
    const updateCommentByStaff = useCallback(async (commentId: number, commentText: string): Promise<Comment> => {
        setLoading(true);
        setError(null);
        try {
            const updatedComment = await commentService.updateCommentByStaff(commentId, commentText);

            // Aktualizuj lokalny stan
            setComments(prevComments =>
                prevComments.map(comment =>
                    comment.id === commentId
                        ? { ...comment, text: commentText }
                        : comment
                )
            );

            return updatedComment;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    // Usuwanie komentarza przez staff
    const deleteCommentByStaff = useCallback(async (commentId: number): Promise<boolean> => {
        setLoading(true);
        setError(null);
        try {
            await commentService.deleteCommentByStaff(commentId);

            // Usuń z lokalnego stanu
            setComments(prevComments =>
                prevComments.filter(comment => comment.id !== commentId)
            );

            return true;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    // Pobieranie szczegółów komentarza
    const getCommentDetails = useCallback(async (commentId: number): Promise<Comment> => {
        setLoading(true);
        setError(null);
        try {
            const details = await commentService.getCommentDetails(commentId);
            return details;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        comments,
        loading,
        error,
        pagination,
        fetchAllComments,
        updateCommentByStaff,
        deleteCommentByStaff,
        getCommentDetails,
        setError,
        setComments
    };
};

// Hook dla komentarzy filmu (dla zwykłych użytkowników)
interface UseMovieCommentsReturn {
    comments: Comment[];
    loading: boolean;
    error: string | null;
    pagination: CommentsPagination;
    fetchMovieComments: (params?: CommentFilters) => Promise<void>;
    addComment: (commentText: string) => Promise<Comment>;
    updateComment: (commentId: number, commentText: string) => Promise<Comment>;
    deleteComment: (commentId: number) => Promise<boolean>;
    setError: (error: string | null) => void;
}

export const useMovieComments = (movieId?: number): UseMovieCommentsReturn => {
    const [comments, setComments] = useState<Comment[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [pagination, setPagination] = useState<CommentsPagination>({
        total: 0,
        total_pages: 0,
        page: 1,
        per_page: 10
    });

    const fetchMovieComments = useCallback(async (params: CommentFilters = {}) => {
        if (!movieId) return;

        setLoading(true);
        setError(null);
        try {
            const data = await commentService.getMovieComments(movieId, params);
            setComments(data.comments || []);
            setPagination(data.pagination || {
                total: 0,
                total_pages: 0,
                page: 1,
                per_page: 10
            });
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [movieId]);

    const addComment = useCallback(async (commentText: string): Promise<Comment> => {
        if (!movieId) throw new Error('Movie ID is required');

        setLoading(true);
        setError(null);
        try {
            const newComment = await commentService.addComment(movieId, commentText);
            setComments(prevComments => [newComment, ...prevComments]);
            return newComment;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [movieId]);

    const updateComment = useCallback(async (commentId: number, commentText: string): Promise<Comment> => {
        setLoading(true);
        setError(null);
        try {
            const updatedComment = await commentService.updateComment(commentId, commentText);
            setComments(prevComments =>
                prevComments.map(comment =>
                    comment.id === commentId
                        ? { ...comment, text: commentText }
                        : comment
                )
            );
            return updatedComment;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const deleteComment = useCallback(async (commentId: number): Promise<boolean> => {
        setLoading(true);
        setError(null);
        try {
            await commentService.deleteComment(commentId);
            setComments(prevComments =>
                prevComments.filter(comment => comment.id !== commentId)
            );
            return true;
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    // Automatyczne ładowanie komentarzy przy zmianie movieId
    useEffect(() => {
        if (movieId) {
            fetchMovieComments();
        }
    }, [fetchMovieComments, movieId]);

    return {
        comments,
        loading,
        error,
        pagination,
        fetchMovieComments,
        addComment,
        updateComment,
        deleteComment,
        setError
    };
};

// Hook dla statystyk komentarzy
interface UseCommentsStatisticsReturn {
    statistics: CommentsStatistics | null;
    loading: boolean;
    error: string | null;
    fetchStatistics: () => Promise<void>;
}

export const useCommentsStatistics = (): UseCommentsStatisticsReturn => {
    const [statistics, setStatistics] = useState<CommentsStatistics | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const fetchStatistics = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const stats = await commentService.getCommentsStatistics();
            setStatistics(stats);
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        statistics,
        loading,
        error,
        fetchStatistics
    };
};

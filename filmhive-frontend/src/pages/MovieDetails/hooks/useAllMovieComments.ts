import { useState, useEffect, useCallback } from 'react';
import { CommentService, Comment, CommentResponse } from '../services/commentService';

interface UseAllMovieCommentsProps {
    movieId: number;
    initialPage?: number;
    perPage?: number;
    initialSortBy?: string;
    initialSortOrder?: string;
}

export const useAllMovieComments = ({
    movieId,
    initialPage = 1,
    perPage = 10,
    initialSortBy = 'created_at',
    initialSortOrder = 'desc'
}: UseAllMovieCommentsProps) => {
    const [comments, setComments] = useState<Comment[]>([]);
    const [pagination, setPagination] = useState({
        total: 0,
        total_pages: 0,
        page: initialPage,
        per_page: perPage
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [sortBy, setSortBy] = useState(initialSortBy);
    const [sortOrder, setSortOrder] = useState(initialSortOrder);

    const fetchComments = useCallback(async (page: number = pagination.page) => {
        if (!movieId) return;

        setIsLoading(true);
        setError(null);

        try {
            const result = await CommentService.getMovieCommentsWithRatings(
                movieId,
                page,
                perPage,
                sortBy,
                sortOrder
            );

            setComments(result.comments);
            setPagination(result.pagination);
        } catch (err) {
            console.error('Błąd podczas pobierania komentarzy:', err);
            setError(err instanceof Error ? err.message : 'Wystąpił nieznany błąd');
        } finally {
            setIsLoading(false);
        }
    }, [movieId, perPage, pagination.page, sortBy, sortOrder]);

    useEffect(() => {
        fetchComments(initialPage);
    }, [fetchComments, initialPage, sortBy, sortOrder]);

    const changePage = useCallback((newPage: number) => {
        if (newPage < 1 || newPage > pagination.total_pages || isLoading) return;
        fetchComments(newPage);
    }, [fetchComments, pagination.total_pages, isLoading]);

    const changeSort = useCallback((newSortBy: string, newSortOrder: string) => {
        setSortBy(newSortBy);
        setSortOrder(newSortOrder);
    }, []);

    return {
        comments,
        pagination,
        isLoading,
        error,
        changePage,
        changeSort,
        sortBy,
        sortOrder,
        refreshComments: fetchComments
    };
};

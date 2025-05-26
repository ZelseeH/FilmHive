import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { useComments } from '../../hooks/useComments';
import Pagination from '../../../../components/ui/Pagination';
import EditCommentModal from './EditCommentModal';
import DeleteCommentModal from './DeleteCommentModal';
import styles from './CommentsManagePage.module.css';
import { Comment } from '../../types/comment';

const CommentsManagePage: React.FC = () => {
    const { user: currentUser } = useAuth();
    const {
        comments,
        loading,
        error,
        pagination,
        fetchAllComments,
        updateCommentByStaff,
        deleteCommentByStaff,
        setError
    } = useComments();

    const [currentPage, setCurrentPage] = useState<number>(1);
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [dateFrom, setDateFrom] = useState<string>('');
    const [dateTo, setDateTo] = useState<string>('');
    const [sortBy, setSortBy] = useState<'created_at' | 'movie_title' | 'username'>('created_at');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
    const [editingComment, setEditingComment] = useState<Comment | null>(null);
    const [deletingComment, setDeletingComment] = useState<Comment | null>(null);
    const perPage = 20;

    const fetchComments = async (page: number = 1) => {
        try {
            await fetchAllComments({
                page,
                per_page: perPage,
                search: searchQuery || undefined,
                date_from: dateFrom || undefined,
                date_to: dateTo || undefined,
                sort_by: sortBy,
                sort_order: sortOrder
            });
        } catch (err: any) {
            console.error('Error fetching comments:', err);
        }
    };

    useEffect(() => {
        fetchComments();
    }, [sortBy, sortOrder]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setCurrentPage(1);
        fetchComments(1);
    };

    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage);
        fetchComments(newPage);
    };

    const handleEditComment = (comment: Comment) => {
        setEditingComment(comment);
    };

    const handleDeleteComment = (comment: Comment) => {
        setDeletingComment(comment);
    };

    const handleEditSubmit = async (commentId: number, newText: string) => {
        try {
            await updateCommentByStaff(commentId, newText);
            setEditingComment(null);
            fetchComments(currentPage);
        } catch (err: any) {
            console.error('Error updating comment:', err);
        }
    };

    const handleDeleteConfirm = async (commentId: number) => {
        try {
            await deleteCommentByStaff(commentId);
            setDeletingComment(null);
            fetchComments(currentPage);
        } catch (err: any) {
            console.error('Error deleting comment:', err);
        }
    };

    const formatDate = (dateString: string): string => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('pl-PL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    };

    const truncateText = (text: string, maxLength: number = 100): string => {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Zarządzanie Komentarzami</h1>
                <p className={styles.description}>
                    Przeglądaj, filtruj i zarządzaj komentarzami w systemie.
                </p>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div className={styles.filtersContainer}>
                <form onSubmit={handleSearch} className={styles.searchForm}>
                    <input
                        type="text"
                        placeholder="Szukaj po nazwie filmu, użytkowniku lub treści komentarza"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className={styles.searchInput}
                    />
                    <button type="submit" className={styles.searchButton}>Szukaj</button>
                </form>

                <div className={styles.dateFilters}>
                    <div className={styles.dateFilter}>
                        <label>Od:</label>
                        <input
                            type="date"
                            value={dateFrom}
                            onChange={(e) => setDateFrom(e.target.value)}
                            className={styles.dateInput}
                        />
                    </div>
                    <div className={styles.dateFilter}>
                        <label>Do:</label>
                        <input
                            type="date"
                            value={dateTo}
                            onChange={(e) => setDateTo(e.target.value)}
                            className={styles.dateInput}
                        />
                    </div>
                </div>

                <div className={styles.sortControls}>
                    <div className={styles.sortFilter}>
                        <label>Sortuj po:</label>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as 'created_at' | 'movie_title' | 'username')}
                            className={styles.select}
                        >
                            <option value="created_at">Data utworzenia</option>
                            <option value="movie_title">Tytuł filmu</option>
                            <option value="username">Nazwa użytkownika</option>
                        </select>
                    </div>
                    <div className={styles.sortFilter}>
                        <label>Kolejność:</label>
                        <select
                            value={sortOrder}
                            onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
                            className={styles.select}
                        >
                            <option value="desc">Malejąco</option>
                            <option value="asc">Rosnąco</option>
                        </select>
                    </div>
                </div>
            </div>

            {loading && comments.length === 0 ? (
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Ładowanie komentarzy...</p>
                </div>
            ) : (
                <>
                    <div className={styles.tableContainer}>
                        <table className={styles.commentsTable}>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Użytkownik</th>
                                    <th>Film</th>
                                    <th>Treść komentarza</th>
                                    <th>Data utworzenia</th>
                                    <th>Akcje</th>
                                </tr>
                            </thead>
                            <tbody>
                                {comments.map(comment => (
                                    <tr key={comment.id}>
                                        <td>
                                            <span className={styles.truncateText} title={comment.id.toString()}>
                                                {comment.id}
                                            </span>
                                        </td>
                                        <td>
                                            <div className={styles.userInfo}>
                                                {comment.user?.profile_picture && (
                                                    <img
                                                        src={comment.user.profile_picture}
                                                        alt={comment.user.username}
                                                        className={styles.userAvatar}
                                                    />
                                                )}
                                                <span className={styles.truncateText} title={comment.user?.username}>
                                                    {comment.user?.username || 'Nieznany użytkownik'}
                                                </span>
                                            </div>
                                        </td>
                                        <td>
                                            <span className={styles.truncateText} title={comment.movie?.title}>
                                                {comment.movie?.title || 'Nieznany film'}
                                            </span>
                                        </td>
                                        <td>
                                            <span
                                                className={styles.commentText}
                                                title={comment.text}
                                            >
                                                {truncateText(comment.text)}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={styles.truncateText} title={formatDate(comment.created_at)}>
                                                {formatDate(comment.created_at)}
                                            </span>
                                        </td>
                                        <td>
                                            <div className={styles.actionButtons}>
                                                <button
                                                    onClick={() => handleEditComment(comment)}
                                                    className={styles.editBtn}
                                                    title="Edytuj komentarz"
                                                >
                                                    Edytuj
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteComment(comment)}
                                                    className={styles.deleteBtn}
                                                    title="Usuń komentarz"
                                                >
                                                    Usuń
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {pagination.total_pages > 1 && (
                        <div className={styles.paginationContainer}>
                            <Pagination
                                currentPage={currentPage}
                                totalPages={pagination.total_pages}
                                onPageChange={handlePageChange}
                            />
                        </div>
                    )}

                    <div className={styles.commentStats}>
                        <p>Łączna liczba komentarzy: <span className={styles.statValue}>{pagination.total}</span></p>
                    </div>
                </>
            )}

            {editingComment && (
                <EditCommentModal
                    comment={editingComment}
                    onClose={() => setEditingComment(null)}
                    onSubmit={handleEditSubmit}
                />
            )}

            {deletingComment && (
                <DeleteCommentModal
                    comment={deletingComment}
                    onClose={() => setDeletingComment(null)}
                    onConfirm={handleDeleteConfirm}
                />
            )}
        </div>
    );
};

export default CommentsManagePage;

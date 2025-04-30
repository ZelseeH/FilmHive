import React from 'react';
import { useAllMovieComments } from '../../hooks/useAllMovieComments';
import styles from './AllMovieComments.module.css';

interface AllMovieCommentsProps {
    movieId: number;
}

const AllMovieComments: React.FC<AllMovieCommentsProps> = ({ movieId }) => {
    const {
        comments,
        pagination,
        isLoading,
        error,
        changePage,
        changeSort,
        sortBy,
        sortOrder,
    } = useAllMovieComments({
        movieId,
        perPage: 10,
    });

    const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        if (value === 'newest') {
            changeSort('created_at', 'desc');
        } else if (value === 'oldest') {
            changeSort('created_at', 'asc');
        } else if (value === 'highest_rating') {
            changeSort('rating', 'desc');
        } else if (value === 'lowest_rating') {
            changeSort('rating', 'asc');
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric' });
    };

    const getCurrentSortValue = () => {
        if (sortBy === 'created_at') {
            return sortOrder === 'desc' ? 'newest' : 'oldest';
        } else {
            return sortOrder === 'desc' ? 'highest_rating' : 'lowest_rating';
        }
    };

    return (
        <>
            <h2 className={styles['title']}>Wszystkie komentarze ({pagination.total})</h2>

            <div className={styles['sorting-controls']}>
                <label htmlFor="sort-select">Sortuj według:</label>
                <select
                    id="sort-select"
                    value={getCurrentSortValue()}
                    onChange={handleSortChange}
                    className={styles['sort-select']}
                    disabled={isLoading}
                >
                    <option value="newest">Najnowsze</option>
                    <option value="oldest">Najstarsze</option>
                    <option value="highest_rating">Najwyższa ocena</option>
                    <option value="lowest_rating">Najniższa ocena</option>
                </select>
            </div>

            {error && <p className={styles['error']}>{error}</p>}

            {isLoading && comments.length === 0 ? (
                <div className={styles['loading']}>Ładowanie komentarzy...</div>
            ) : comments.length > 0 ? (
                <>
                    <div className={styles['comments-list']}>
                        {comments.map((comment) => (
                            <div key={comment.comment_id} className={styles['comment-item']}>
                                <div className={styles['comment-header']}>
                                    <div className={styles['user-info']}>
                                        {comment.user?.profile_picture && (
                                            <img
                                                src={comment.user.profile_picture}
                                                alt={comment.user?.username}
                                                className={styles['user-avatar']}
                                            />
                                        )}
                                        <span className={styles['username']}>{comment.user?.username || 'Użytkownik'}</span>
                                    </div>
                                    <div className={styles['comment-meta']}>
                                        <div className={styles['rating-date-group']}>
                                            {comment.user_rating !== null && comment.user_rating !== undefined && (
                                                <div className={styles['user-rating']}>
                                                    <span className={styles['rating-value']}>{comment.user_rating}</span>
                                                    <span className={styles['rating-icon']}>★</span>
                                                </div>
                                            )}
                                            <span className={styles['date']}>{formatDate(comment.created_at)}</span>
                                        </div>
                                    </div>
                                </div>
                                <p className={styles['comment-text']}>{comment.text}</p>
                            </div>
                        ))}

                    </div>

                    {pagination.total_pages > 1 && (
                        <div className={styles['pagination']}>
                            <button
                                onClick={() => changePage(pagination.page - 1)}
                                disabled={pagination.page === 1 || isLoading}
                                className={styles['page-button']}
                            >
                                « Poprzednia
                            </button>

                            <div className={styles['page-numbers']}>
                                {pagination.total_pages <= 7 ? (
                                    Array.from({ length: pagination.total_pages }, (_, i) => i + 1).map((page) => (
                                        <button
                                            key={page}
                                            onClick={() => changePage(page)}
                                            disabled={isLoading}
                                            className={`${styles['page-button']} ${page === pagination.page ? styles['active-page'] : ''}`}
                                        >
                                            {page}
                                        </button>
                                    ))
                                ) : (
                                    <>
                                        <button
                                            onClick={() => changePage(1)}
                                            disabled={isLoading}
                                            className={`${styles['page-button']} ${1 === pagination.page ? styles['active-page'] : ''}`}
                                        >
                                            1
                                        </button>

                                        {pagination.page > 3 && <span className={styles['ellipsis']}>...</span>}

                                        {Array.from({ length: pagination.total_pages }, (_, i) => i + 1)
                                            .filter((page) => Math.abs(page - pagination.page) <= 1 && page !== 1 && page !== pagination.total_pages)
                                            .map((page) => (
                                                <button
                                                    key={page}
                                                    onClick={() => changePage(page)}
                                                    disabled={isLoading}
                                                    className={`${styles['page-button']} ${page === pagination.page ? styles['active-page'] : ''}`}
                                                >
                                                    {page}
                                                </button>
                                            ))}

                                        {pagination.page < pagination.total_pages - 2 && <span className={styles['ellipsis']}>...</span>}

                                        <button
                                            onClick={() => changePage(pagination.total_pages)}
                                            disabled={isLoading}
                                            className={`${styles['page-button']} ${pagination.total_pages === pagination.page ? styles['active-page'] : ''
                                                }`}
                                        >
                                            {pagination.total_pages}
                                        </button>
                                    </>
                                )}
                            </div>

                            <button
                                onClick={() => changePage(pagination.page + 1)}
                                disabled={pagination.page === pagination.total_pages || isLoading}
                                className={styles['page-button']}
                            >
                                Następna »
                            </button>
                        </div>
                    )}
                </>
            ) : (
                <p className={styles['no-comments']}>Brak komentarzy dla tego filmu.</p>
            )}
        </>
    );
};

export default AllMovieComments;
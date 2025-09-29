import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAllMovieComments } from '../../hooks/useAllMovieComments';
import ThreadModal from './ThreadModal';
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

    const [selectedCommentId, setSelectedCommentId] = useState<number | null>(null);
    const [repliesData, setRepliesData] = useState<{ [key: number]: { count: number, firstReply: any } }>({});

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
        const cleanDate = dateString.replace('Z', '').replace('T', ' ');
        const date = new Date(cleanDate);
        return date.toLocaleDateString('pl-PL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getRatingValue = (rating: any): number | null => {
        if (!rating) return null;
        if (typeof rating === 'number') return rating;
        if (typeof rating === 'object' && rating.rating) return rating.rating;
        return null;
    };

    const fetchFirstReply = async (commentId: number) => {
        try {
            const response = await fetch(`/api/comments/${commentId}/replies`);
            const data = await response.json();

            if (data.success) {
                setRepliesData(prev => ({
                    ...prev,
                    [commentId]: {
                        count: data.data.replies_count,
                        firstReply: data.data.replies[0] || null
                    }
                }));
                return data.data.replies; // Zwróć replies dla hash checking
            }
        } catch (error) {
            console.error('Błąd podczas pobierania odpowiedzi:', error);
        }
        return [];
    };

    useEffect(() => {
        if (comments.length > 0) {
            comments.forEach(comment => {
                fetchFirstReply(comment.id);
            });
        }
    }, [comments]);

    // ✨ NOWA LOGIKA - Auto-otwieranie ThreadModal dla #reply-
    useEffect(() => {
        const hash = window.location.hash;
        console.log('🔍 AllMovieComments - Checking hash:', hash);

        if (hash.startsWith('#reply-') && comments.length > 0) {
            const replyId = parseInt(hash.replace('#reply-', ''));
            console.log('🔍 AllMovieComments - Looking for reply ID:', replyId);

            const checkComments = async () => {
                for (const comment of comments) {
                    try {
                        const response = await fetch(`/api/comments/${comment.id}/replies`);
                        const data = await response.json();

                        if (data.success && data.data.replies) {
                            const foundReply = data.data.replies.find((reply: any) => reply.id === replyId);
                            if (foundReply) {
                                console.log('🔍 AllMovieComments - Found reply in comment:', comment.id);
                                console.log('🔍 AllMovieComments - Opening ThreadModal for comment:', comment.id);
                                setSelectedCommentId(comment.id);

                                // Usuń hash z URL żeby uniknąć konfliktów ze ScrollAnchor
                                window.history.replaceState(null, '', window.location.pathname);
                                return;
                            }
                        }
                    } catch (error) {
                        console.error('Error checking replies:', error);
                    }
                }
            };

            checkComments();
        }
    }, [comments]);

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
                        {comments.map((comment) => {
                            const replyData = repliesData[comment.id];
                            const commentRating = getRatingValue(comment.user_rating);
                            const hasReplies = replyData?.count > 0;

                            return (
                                <div key={comment.id} className={styles['comment-thread']}>
                                    {/* GŁÓWNY KOMENTARZ Z ID */}
                                    <div
                                        id={`comment-${comment.id}`}
                                        className={styles['comment-item']}
                                    >
                                        <div className={styles['comment-header']}>
                                            <div className={styles['user-info']}>
                                                {comment.user?.profile_picture ? (
                                                    <Link to={`/profile/${comment.user.username}`}>
                                                        <img
                                                            src={comment.user.profile_picture}
                                                            alt={comment.user?.username}
                                                            className={styles['user-avatar']}
                                                            style={{ cursor: 'pointer' }}
                                                        />
                                                    </Link>
                                                ) : (
                                                    <div className={styles['default-avatar']}>
                                                        {comment.user?.username?.charAt(0)?.toUpperCase() || 'U'}
                                                    </div>
                                                )}
                                                <span className={styles['username']}>{comment.user?.username || 'Użytkownik'}</span>
                                            </div>
                                            <div className={styles['comment-meta']}>
                                                <div className={styles['rating-date-group']}>
                                                    {commentRating !== null && (
                                                        <div className={styles['user-rating']}>
                                                            <span className={styles['rating-value']}>{commentRating}</span>
                                                            <span className={styles['rating-icon']}>★</span>
                                                        </div>
                                                    )}
                                                    <span className={styles['date']}>{formatDate(comment.created_at)}</span>
                                                </div>
                                            </div>
                                        </div>

                                        <p className={styles['comment-text']}>{comment.text}</p>
                                    </div>

                                    {/* PIERWSZA ODPOWIEDŹ Z ID */}
                                    {replyData?.firstReply && (
                                        <div
                                            id={`reply-${replyData.firstReply.id}`}
                                            className={styles['first-reply']}
                                        >
                                            <div className={styles['reply-header']}>
                                                <div className={styles['user-info']}>
                                                    {replyData.firstReply.reply_user?.profile_picture ? (
                                                        <Link to={`/profile/${replyData.firstReply.reply_user.username}`}>
                                                            <img
                                                                src={replyData.firstReply.reply_user.profile_picture}
                                                                alt={replyData.firstReply.reply_user.username}
                                                                className={styles['user-avatar']}
                                                                style={{ cursor: 'pointer' }}
                                                            />
                                                        </Link>
                                                    ) : (
                                                        <div className={styles['default-avatar']}>
                                                            {replyData.firstReply.reply_user?.username?.charAt(0)?.toUpperCase() || 'U'}
                                                        </div>
                                                    )}
                                                    <span className={styles['reply-username']}>
                                                        {replyData.firstReply.reply_user?.username || 'Użytkownik'}
                                                    </span>
                                                </div>

                                                <div className={styles['comment-meta']}>
                                                    <div className={styles['rating-date-group']}>
                                                        {getRatingValue(replyData.firstReply.user_rating) !== null && (
                                                            <div className={styles['user-rating']}>
                                                                <span className={styles['rating-value']}>
                                                                    {getRatingValue(replyData.firstReply.user_rating)}
                                                                </span>
                                                                <span className={styles['rating-icon']}>★</span>
                                                            </div>
                                                        )}
                                                        <span className={styles['reply-date']}>
                                                            {formatDate(replyData.firstReply.created_at)}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <p className={styles['reply-text']}>{replyData.firstReply.text}</p>

                                            {/* PRZYCISK DO WĄTKU */}
                                            <div className={styles['first-reply-actions']}>
                                                <button
                                                    onClick={() => setSelectedCommentId(comment.id)}
                                                    className={styles['thread-button']}
                                                >
                                                    Zobacz wątek ({replyData.count})
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    {/* PAGINACJA */}
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
                                            className={`${styles['page-button']} ${pagination.total_pages === pagination.page ? styles['active-page'] : ''}`}
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

            {selectedCommentId && (
                <ThreadModal
                    commentId={selectedCommentId}
                    onClose={() => setSelectedCommentId(null)}
                />
            )}
        </>
    );
};

export default AllMovieComments;

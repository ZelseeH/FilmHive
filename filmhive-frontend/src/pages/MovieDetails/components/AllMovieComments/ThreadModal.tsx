import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { Link } from 'react-router-dom';
import { threadService, replyService } from '../../services/replyService';
import { ThreadData } from '../../types/replies';
import ReplyForm from './Reply/ReplyForm';
import ReplyList from './Reply/ReplyList';
import styles from './ThreadModal.module.css';

interface ThreadModalProps {
    commentId: number;
    onClose: () => void;
}

const ThreadModal: React.FC<ThreadModalProps> = ({ commentId, onClose }) => {
    const { user, getToken, openLoginModal } = useAuth();
    const [threadData, setThreadData] = useState<ThreadData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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

    // Helper funkcja do pobierania tekstu komentarza
    const getMainCommentText = () => {
        if (!threadData?.main_comment) return '';

        // Sprawdź różne możliwe nazwy pól
        return threadData.main_comment.comment_text ||
            (threadData.main_comment as any).text ||
            '';
    };

    // POPRAWIONA FUNKCJA: Pobiera ID użytkownika ostatniej odpowiedzi z właściwymi typami
    const getLastReplyUserId = (): number | undefined => {
        if (!threadData?.replies || threadData.replies.length === 0) {
            return undefined;
        }

        const lastReply = threadData.replies[threadData.replies.length - 1];

        // Sprawdź różne możliwe nazwy pól dla ID użytkownika - używaj type assertion
        return (lastReply as any).reply_user_id ||
            (lastReply as any).id_reply ||
            (lastReply as any).user_id ||
            lastReply.reply_user?.user_id;
    };

    const fetchThread = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await threadService.getThread(commentId);
            setThreadData(data);
        } catch (err) {
            console.error('Błąd podczas ładowania wątku:', err);
            setError('Błąd podczas ładowania wątku');
        } finally {
            setIsLoading(false);
        }
    };

    const handleAddReply = async (replyText: string) => {
        if (!user) {
            openLoginModal();
            return false;
        }

        const token = getToken();
        try {
            await replyService.addReply(commentId, replyText, token!);
            await fetchThread(); // Odśwież dane po dodaniu odpowiedzi
            return true;
        } catch (error) {
            console.error('Błąd podczas dodawania odpowiedzi:', error);
            return false;
        }
    };

    const handleEditReply = async (replyId: number, newText: string) => {
        try {
            const token = getToken();
            if (token) {
                await replyService.updateReply(replyId, newText, token);
                await fetchThread();
            }
        } catch (error) {
            console.error('Błąd podczas edycji odpowiedzi:', error);
            throw error;
        }
    };

    const handleDeleteReply = async (replyId: number) => {
        try {
            const token = getToken();
            if (token) {
                await replyService.deleteReply(replyId, token);
                await fetchThread();
            }
        } catch (error) {
            console.error('Błąd podczas usuwania odpowiedzi:', error);
            throw error;
        }
    };

    useEffect(() => {
        fetchThread();
    }, [commentId]);

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                    <div className={styles.headerContent}>
                        <h2>Wątek komentarza</h2>
                        <p className={styles.headerSubtitle}>
                            {threadData?.replies_count || 0} {(threadData?.replies_count || 0) === 1 ? 'odpowiedź' : 'odpowiedzi'}
                        </p>
                    </div>
                    <button className={styles.closeButton} onClick={onClose}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                        </svg>
                    </button>
                </div>

                <div className={styles.modalBody}>
                    {isLoading ? (
                        <div className={styles.loadingContainer}>
                            <div className={styles.spinner}></div>
                            <p>Ładowanie wątku...</p>
                        </div>
                    ) : error ? (
                        <div className={styles.errorContainer}>
                            <span className={styles.errorIcon}>⚠️</span>
                            <p>{error}</p>
                        </div>
                    ) : (
                        <>
                            {threadData?.main_comment && (
                                <div className={styles.mainCommentWrapper}>
                                    <div className={styles.commentItem}>
                                        <div className={styles.commentHeader}>
                                            <div className={styles.userInfo}>
                                                {threadData.main_comment.user?.profile_picture ? (
                                                    <Link to={`/profile/${threadData.main_comment.user.username}`}>
                                                        <img
                                                            src={threadData.main_comment.user.profile_picture}
                                                            alt={threadData.main_comment.user.username}
                                                            className={styles.userAvatar}
                                                        />
                                                    </Link>
                                                ) : (
                                                    <div className={styles.defaultAvatar}>
                                                        {threadData.main_comment.user?.username?.charAt(0)?.toUpperCase() || 'U'}
                                                    </div>
                                                )}
                                                <span className={styles.username}>
                                                    {threadData.main_comment.user?.username || 'Użytkownik'}
                                                </span>
                                            </div>

                                            <div className={styles.commentMeta}>
                                                <div className={styles.ratingDateGroup}>
                                                    {getRatingValue(threadData.main_comment.user_rating) !== null && (
                                                        <div className={styles.userRating}>
                                                            <span className={styles.ratingValue}>
                                                                {getRatingValue(threadData.main_comment.user_rating)}
                                                            </span>
                                                            <span className={styles.ratingIcon}>★</span>
                                                        </div>
                                                    )}
                                                    <span className={styles.date}>
                                                        {formatDate(threadData.main_comment.created_at)}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        <p className={styles.commentText}>
                                            {getMainCommentText()}
                                        </p>
                                    </div>
                                </div>
                            )}

                            <div className={styles.repliesSection}>
                                <div className={styles.repliesHeader}>
                                    <h3>Odpowiedzi</h3>
                                    <span className={styles.repliesCount}>{threadData?.replies_count || 0}</span>
                                </div>
                                <ReplyList
                                    replies={threadData?.replies || []}
                                    onEdit={handleEditReply}
                                    onDelete={handleDeleteReply}
                                />
                            </div>

                            <div className={styles.replyFormWrapper}>
                                {user ? (
                                    <div className={styles.replyFormSection}>
                                        <h4>Dodaj swoją odpowiedź</h4>
                                        <ReplyForm
                                            onSubmit={handleAddReply}
                                            onCancel={() => { }}
                                            lastReplyUserId={getLastReplyUserId()}
                                            currentUserId={typeof user.id === 'string' ? parseInt(user.id, 10) : user.id}
                                        />
                                    </div>
                                ) : (
                                    <div className={styles.loginPrompt}>
                                        <div className={styles.loginContent}>
                                            <div>
                                                <p>Zaloguj się, aby dołączyć do dyskusji</p>
                                                <button onClick={openLoginModal} className={styles.loginButton}>
                                                    Zaloguj się
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ThreadModal;

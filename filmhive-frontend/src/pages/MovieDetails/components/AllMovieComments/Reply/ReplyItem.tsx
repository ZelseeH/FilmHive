import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../../../contexts/AuthContext';
import { Reply } from '../../../types/replies';
import styles from './ReplyItem.module.css';

interface ReplyItemProps {
    reply: Reply;
    onDelete?: (replyId: number) => Promise<void>;
    onEdit?: (replyId: number, newText: string) => Promise<void>;
}

const ReplyItem: React.FC<ReplyItemProps> = ({ reply, onDelete, onEdit }) => {
    const { user } = useAuth();
    const [isEditing, setIsEditing] = useState(false);
    const [editText, setEditText] = useState(reply.text);
    const [isLoading, setIsLoading] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    const replyId = reply.id;

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

    const handleSave = () => {
        if (!editText.trim() || !onEdit) return;

        setIsLoading(true);
        onEdit(replyId, editText.trim())
            .then(() => {
                setIsEditing(false);
            })
            .catch((error) => {
                console.error('Błąd podczas edytowania odpowiedzi:', error);
                window.alert('Nie udało się zapisać zmian');
            })
            .finally(() => {
                setIsLoading(false);
            });
    };

    const handleDeleteConfirm = () => {
        if (!onDelete) return;

        setIsLoading(true);
        onDelete(replyId)
            .then(() => {
                setShowDeleteConfirm(false);
            })
            .catch((error) => {
                console.error('Błąd podczas usuwania odpowiedzi:', error);
                window.alert('Nie udało się usunąć odpowiedzi');
            })
            .finally(() => {
                setIsLoading(false);
            });
    };

    const handleCancel = () => {
        setEditText(reply.text);
        setIsEditing(false);
    };

    const isOwner = user && (
        Number(user.id) === reply.reply_user_id ||
        String(user.id) === String(reply.reply_user_id)
    );

    return (
        <div className={styles.replyItem}>
            <div className={styles.commentHeader}>
                <div className={styles.userInfo}>
                    {reply.reply_user?.profile_picture ? (
                        <Link to={`/profile/${reply.reply_user.username}`}>
                            <img
                                src={reply.reply_user.profile_picture}
                                alt={reply.reply_user.username}
                                className={styles.userAvatar}
                                style={{ cursor: 'pointer' }}
                            />
                        </Link>
                    ) : (
                        <div className={styles.defaultAvatar}>
                            {reply.reply_user?.username?.charAt(0)?.toUpperCase() || 'U'}
                        </div>
                    )}
                    <span className={styles.username}>
                        {reply.reply_user?.username || 'Użytkownik'}
                    </span>
                </div>

                <div className={styles.commentMeta}>
                    <div className={styles.ratingDateGroup}>
                        {reply.user_rating !== null && reply.user_rating !== undefined && (
                            <div className={styles.userRating}>
                                <span className={styles.ratingValue}>{reply.user_rating}</span>
                                <span className={styles.ratingIcon}>★</span>
                            </div>
                        )}
                        <span className={styles.date}>{formatDate(reply.created_at)}</span>
                    </div>
                </div>
            </div>

            {isEditing ? (
                <div className={styles.editContainer}>
                    <textarea
                        className={styles.textarea}
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        maxLength={500}
                        placeholder="Edytuj swoją odpowiedź..."
                        disabled={isLoading}
                    />
                    <div className={styles.editActions}>
                        <button
                            onClick={handleSave}
                            className={styles.saveBtn}
                            disabled={isLoading || !editText.trim()}
                        >
                            {isLoading ? 'Zapisywanie...' : 'Zapisz'}
                        </button>
                        <button
                            onClick={handleCancel}
                            className={styles.cancelBtn}
                            disabled={isLoading}
                        >
                            Anuluj
                        </button>
                    </div>
                </div>
            ) : (
                <>
                    <p className={styles.commentText}>{reply.text}</p>
                    {isOwner && (
                        <div className={styles.actions}>
                            <button
                                onClick={() => setIsEditing(true)}
                                className={styles.editBtn}
                                disabled={isLoading}
                            >
                                Edytuj
                            </button>
                            {!showDeleteConfirm ? (
                                <button
                                    onClick={() => setShowDeleteConfirm(true)}
                                    className={styles.deleteBtn}
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Usuwanie...' : 'Usuń'}
                                </button>
                            ) : (
                                <div className={styles.confirmActions}>
                                    <span className={styles.confirmText}>Na pewno?</span>
                                    <button
                                        onClick={handleDeleteConfirm}
                                        className={styles.confirmBtn}
                                        disabled={isLoading}
                                    >
                                        Tak
                                    </button>
                                    <button
                                        onClick={() => setShowDeleteConfirm(false)}
                                        className={styles.cancelConfirmBtn}
                                        disabled={isLoading}
                                    >
                                        Nie
                                    </button>
                                </div>
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default ReplyItem;

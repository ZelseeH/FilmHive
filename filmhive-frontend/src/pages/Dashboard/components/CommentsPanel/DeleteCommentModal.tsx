import React, { useState } from 'react';
import { Comment } from '../../types/comment';
import styles from './DeleteCommentModal.module.css';

interface DeleteCommentModalProps {
    comment: Comment;
    onClose: () => void;
    onConfirm: (commentId: number) => Promise<void>;
}

const DeleteCommentModal: React.FC<DeleteCommentModalProps> = ({
    comment,
    onClose,
    onConfirm
}) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleConfirm = async () => {
        setLoading(true);
        setError(null);

        try {
            await onConfirm(comment.id);
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas usuwania komentarza');
        } finally {
            setLoading(false);
        }
    };

    const truncateText = (text: string, maxLength: number = 150): string => {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    };

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                    <h2>Usuń komentarz</h2>
                    <button className={styles.closeButton} onClick={onClose}>×</button>
                </div>

                <div className={styles.warningMessage}>
                    <p>Czy na pewno chcesz usunąć ten komentarz? Ta akcja jest nieodwracalna.</p>
                </div>

                <div className={styles.commentPreview}>
                    <div className={styles.commentInfo}>
                        <p><strong>Użytkownik:</strong> {comment.user?.username}</p>
                        <p><strong>Film:</strong> {comment.movie?.title}</p>
                        <p><strong>Data:</strong> {new Date(comment.created_at).toLocaleString('pl-PL')}</p>
                    </div>
                    <div className={styles.commentText}>
                        <strong>Treść:</strong>
                        <p>"{truncateText(comment.text)}"</p>
                    </div>
                </div>

                {error && <div className={styles.errorMessage}>{error}</div>}

                <div className={styles.modalActions}>
                    <button
                        type="button"
                        onClick={onClose}
                        className={styles.cancelButton}
                        disabled={loading}
                    >
                        Anuluj
                    </button>
                    <button
                        type="button"
                        onClick={handleConfirm}
                        className={styles.deleteButton}
                        disabled={loading}
                    >
                        {loading ? 'Usuwanie...' : 'Usuń komentarz'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DeleteCommentModal;

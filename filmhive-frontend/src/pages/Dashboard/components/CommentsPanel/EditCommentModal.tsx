import React, { useState } from 'react';
import { Comment } from '../../types/comment';
import styles from './EditCommentModal.module.css';

interface EditCommentModalProps {
    comment: Comment;
    onClose: () => void;
    onSubmit: (commentId: number, newText: string) => Promise<void>;
}

const EditCommentModal: React.FC<EditCommentModalProps> = ({
    comment,
    onClose,
    onSubmit
}) => {
    const [commentText, setCommentText] = useState(comment.text);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!commentText.trim()) {
            setError('Treść komentarza nie może być pusta');
            return;
        }

        if (commentText.length > 1000) {
            setError('Komentarz nie może przekraczać 1000 znaków');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            await onSubmit(comment.id, commentText.trim());
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas aktualizacji komentarza');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                    <h2>Edytuj komentarz</h2>
                    <button className={styles.closeButton} onClick={onClose}>×</button>
                </div>

                <div className={styles.commentInfo}>
                    <p><strong>Użytkownik:</strong> {comment.user?.username}</p>
                    <p><strong>Film:</strong> {comment.movie?.title}</p>
                </div>

                {error && <div className={styles.errorMessage}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
                        <label htmlFor="commentText">Treść komentarza:</label>
                        <textarea
                            id="commentText"
                            value={commentText}
                            onChange={(e) => setCommentText(e.target.value)}
                            className={styles.textarea}
                            rows={6}
                            maxLength={1000}
                            disabled={loading}
                        />
                        <div className={styles.charCount}>
                            {commentText.length}/1000 znaków
                        </div>
                    </div>

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
                            type="submit"
                            className={styles.submitButton}
                            disabled={loading || !commentText.trim()}
                        >
                            {loading ? 'Zapisywanie...' : 'Zapisz zmiany'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditCommentModal;

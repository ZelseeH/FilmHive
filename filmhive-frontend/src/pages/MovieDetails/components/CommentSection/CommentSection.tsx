import React, { useState, useEffect } from 'react';
import { useComments, Comment } from '../../hooks/useComments';
import { useAuth } from '../../../../contexts/AuthContext';
import styles from './CommentSection.module.css';

interface CommentSectionProps {
    movieId: number;
}

const MAX_WORDS = 150;

const CommentSection: React.FC<CommentSectionProps> = ({ movieId }) => {
    const { user, getToken, openLoginModal } = useAuth();
    const [commentText, setCommentText] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [wordsLeft, setWordsLeft] = useState(MAX_WORDS);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    const {
        comments,
        isLoading,
        error,
        addComment,
        updateComment,
        deleteComment,
        getUserComment
    } = useComments({ movieId, user, getToken });

    const [userComment, setUserComment] = useState<Comment | null>(null);

    useEffect(() => {
        if (user) {
            const fetchUserComment = async () => {
                const comment = await getUserComment();
                setUserComment(comment);
                if (comment) {
                    setCommentText(comment.text);
                    updateWordsLeft(comment.text);
                }
            };
            fetchUserComment();
        }
    }, [user, getUserComment]);

    const updateWordsLeft = (text: string) => {
        const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
        setWordsLeft(Math.max(0, MAX_WORDS - wordCount));
    };

    const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newText = e.target.value;
        setCommentText(newText);
        updateWordsLeft(newText);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!user) {
            openLoginModal();
            return;
        }

        if (!commentText.trim()) return;

        const wordCount = commentText.trim().split(/\s+/).length;
        if (wordCount > MAX_WORDS) {
            return;
        }

        if (userComment) {
            const updatedComment = await updateComment(userComment.id, commentText);
            if (updatedComment) {
                setUserComment(updatedComment);
                setIsEditing(false);
            }
        } else {
            const newComment = await addComment(commentText);
            if (newComment) {
                setUserComment(newComment);
                setCommentText('');
                setWordsLeft(MAX_WORDS);
            }
        }
    };

    const handleDelete = () => {
        setShowDeleteConfirm(true);
    };

    const confirmDelete = async () => {
        if (userComment) {
            await deleteComment(userComment.id);
            setUserComment(null);
            setCommentText('');
            setWordsLeft(MAX_WORDS);
            setShowDeleteConfirm(false);
        }
    };

    const cancelDelete = () => {
        setShowDeleteConfirm(false);
    };

    const handleEdit = () => {
        setIsEditing(true);
    };

    const handleCancelEdit = () => {
        setIsEditing(false);
        setCommentText(userComment?.text || '');
        updateWordsLeft(userComment?.text || '');
    };

    if (!user) {
        return (
            <div className={styles.commentSection}>
                <p className={styles.loginPrompt}>Zaloguj się, aby dodać komentarz</p>
            </div>
        );
    }

    return (
        <div className={styles.commentSection}>
            {error && <p className={styles.error}>{error}</p>}

            {isLoading ? (
                <p className={styles.loading}>Ładowanie...</p>
            ) : userComment && !isEditing ? (
                <div className={styles.commentDisplay} onClick={handleEdit}>
                    <p className={styles.commentText}>{userComment.text}</p>
                    <div className={styles.commentInfo}>
                        <span className={styles.editHint}>Kliknij, aby edytować</span>
                        <button onClick={(e) => { e.stopPropagation(); handleDelete(); }} className={styles.deleteButton}>
                            <span className={styles.deleteIcon}>🗑️</span>
                        </button>
                    </div>
                </div>
            ) : (
                <form onSubmit={handleSubmit} className={styles.commentForm}>
                    <div className={styles.textareaContainer}>
                        <textarea
                            value={commentText}
                            onChange={handleTextChange}
                            placeholder="Napisz swój komentarz..."
                            className={styles.commentInput}
                            maxLength={1000}
                        />
                        <span className={`${styles.wordCounter} ${wordsLeft === 0 ? styles.wordLimitReached : ''}`}>
                            {wordsLeft}
                        </span>
                    </div>
                    <div className={styles.formActions}>
                        <button
                            type="submit"
                            disabled={isLoading || !commentText.trim() || wordsLeft === 0}
                            className={styles.submitButton}
                        >
                            {isLoading ? "Wysyłanie..." : userComment ? "Zapisz zmiany" : "Dodaj komentarz"}
                        </button>
                        {isEditing && (
                            <button
                                type="button"
                                onClick={handleCancelEdit}
                                className={styles.cancelButton}
                            >
                                Anuluj
                            </button>
                        )}
                    </div>
                </form>
            )}

            {showDeleteConfirm && (
                <div className={styles.deleteConfirmBox}>
                    <p>Czy na pewno chcesz usunąć ten komentarz?</p>
                    <div className={styles.deleteConfirmActions}>
                        <button onClick={confirmDelete} className={styles.confirmDeleteButton}>Tak, usuń</button>
                        <button onClick={cancelDelete} className={styles.cancelDeleteButton}>Anuluj</button>
                    </div>
                </div>
            )}


        </div>
    );
};

export default CommentSection;

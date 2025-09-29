import React, { useState, useEffect } from 'react';
import styles from './ReplyForm.module.css';

interface ReplyFormProps {
    onSubmit: (text: string) => Promise<boolean>;
    onCancel: () => void;
    isLoading?: boolean;
    lastReplyUserId?: number; // ID użytkownika ostatniej odpowiedzi
    currentUserId?: number;    // ID zalogowanego użytkownika
}

const ReplyForm: React.FC<ReplyFormProps> = ({
    onSubmit,
    onCancel,
    isLoading = false,
    lastReplyUserId,
    currentUserId
}) => {
    const [text, setText] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [blockReply, setBlockReply] = useState(false);

    useEffect(() => {
        if (lastReplyUserId !== undefined && currentUserId !== undefined) {
            // Blokuj jeśli ostatnia odpowiedź jest od tego samego użytkownika
            setBlockReply(lastReplyUserId === currentUserId);
        } else {
            setBlockReply(false);
        }
    }, [lastReplyUserId, currentUserId]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (blockReply) {
            setError('Nie możesz odpowiadać bezpośrednio po sobie - to może spamować powiadomienia');
            return;
        }

        if (!text.trim()) {
            setError('Treść odpowiedzi nie może być pusta');
            return;
        }

        try {
            const success = await onSubmit(text);
            if (success) {
                setText('');
            } else {
                setError('Błąd podczas dodawania odpowiedzi');
            }
        } catch {
            setError('Wystąpił niespodziewany błąd');
        }
    };

    return (
        <form className={styles.replyForm} onSubmit={handleSubmit}>
            {error && <div className={styles.error}>{error}</div>}
            <textarea
                className={`${styles.textarea} ${blockReply ? styles.blocked : ''}`}
                placeholder={
                    blockReply
                        ? 'Nie możesz odpowiadać bezpośrednio po sobie'
                        : 'Napisz odpowiedź...'
                }
                value={text}
                onChange={(e) => setText(e.target.value)}
                disabled={isLoading || blockReply}
                maxLength={500}
                title={blockReply ? 'Nie możesz odpowiadać samemu sobie bezpośrednio - zapobiega to spamowaniu powiadomień' : ''}
            />
            <div className={styles.actions}>
                <button
                    type="submit"
                    disabled={isLoading || !text.trim() || blockReply}
                    className={`${styles.submitBtn} ${blockReply ? styles.blocked : ''}`}
                    title={blockReply ? 'Nie można dodać kolejnej odpowiedzi bezpośrednio po swojej' : ''}
                >
                    {isLoading ? 'Dodawanie...' : 'Dodaj odpowiedź'}
                </button>
                <button
                    type="button"
                    onClick={onCancel}
                    disabled={isLoading}
                    className={styles.cancelBtn}
                >
                    Anuluj
                </button>
            </div>
        </form>
    );
};

export default ReplyForm;

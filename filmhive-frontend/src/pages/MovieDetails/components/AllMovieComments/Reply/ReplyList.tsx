import React from 'react';
import ReplyItem from './ReplyItem';
import { Reply } from '../../../types/replies';
import styles from './ReplyList.module.css';

interface ReplyListProps {
    replies: Reply[];
    onEdit?: (replyId: number, newText: string) => Promise<void>;
    onDelete?: (replyId: number) => Promise<void>;
}

const ReplyList: React.FC<ReplyListProps> = ({ replies, onEdit, onDelete }) => {
    if (replies.length === 0) {
        return (
            <div className={styles.noReplies}>
                <p>Brak odpowiedzi. Bądź pierwszy!</p>
            </div>
        );
    }

    return (
        <div className={styles.replyList}>
            {replies.map((reply) => (
                <ReplyItem
                    key={reply.id}
                    reply={reply}
                    onEdit={onEdit}
                    onDelete={onDelete}
                />
            ))}
        </div>
    );
};

export default ReplyList;

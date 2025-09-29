import { Reply } from '../types/replies';
import { ThreadData } from '../types/replies';

export const replyService = {
    async addReply(commentId: number, text: string, token: string): Promise<Reply> {
        const response = await fetch(`/api/comments/${commentId}/replies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ text })
        });

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Błąd podczas dodawania odpowiedzi');
        }

        return data.reply;
    },

    async getReplies(commentId: number): Promise<Reply[]> {
        const response = await fetch(`/api/comments/${commentId}/replies`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Błąd podczas pobierania odpowiedzi');
        }

        return data.data.replies;
    },

    async updateReply(replyId: number, text: string, token: string): Promise<Reply> {
        const response = await fetch(`/api/replies/${replyId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ text })
        });

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Błąd podczas edycji odpowiedzi');
        }

        return data.reply;
    },

    async deleteReply(replyId: number, token: string): Promise<void> {
        const response = await fetch(`/api/replies/${replyId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Błąd podczas usuwania odpowiedzi');
        }
    }
};

export const threadService = {
    async getThread(commentId: number): Promise<ThreadData> {
        const response = await fetch(`/api/comments/${commentId}/thread`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Błąd podczas pobierania wątku');
        }

        return data.data;
    },

    async getThreadPreview(commentId: number): Promise<{
        firstReply: any | null;
        totalCount: number;
    }> {
        const threadData = await this.getThread(commentId);

        return {
            firstReply: threadData.replies.length > 0 ? threadData.replies[0] : null,
            totalCount: threadData.replies_count
        };
    }
};

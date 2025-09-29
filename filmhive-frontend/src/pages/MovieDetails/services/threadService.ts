import { ThreadData } from '../types/replies';

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

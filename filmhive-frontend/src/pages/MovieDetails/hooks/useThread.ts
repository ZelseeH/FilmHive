import { useState, useEffect, useCallback } from 'react';
import { ThreadData } from '../types/replies';
import { threadService } from '../services/threadService';

export const useThread = (commentId: number | null) => {
    const [threadData, setThreadData] = useState<ThreadData | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadThread = useCallback(async () => {
        if (!commentId) {
            setThreadData(null);
            return;
        }

        try {
            setIsLoading(true);
            setError(null);
            const data = await threadService.getThread(commentId);
            setThreadData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Wystąpił błąd');
        } finally {
            setIsLoading(false);
        }
    }, [commentId]);

    useEffect(() => {
        if (commentId) {
            loadThread();
        } else {
            setThreadData(null);
        }
    }, [commentId, loadThread]);

    const refreshThread = useCallback(() => {
        loadThread();
    }, [loadThread]);

    return {
        threadData,
        isLoading,
        error,
        loadThread,
        refreshThread
    };
};

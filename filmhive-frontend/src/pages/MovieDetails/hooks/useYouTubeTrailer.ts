// src/hooks/useYouTubeTrailer.ts
import { useState, useEffect } from 'react';
import { getEmbedUrl } from '../services/youtubeService';

export const useYouTubeTrailer = (url: string) => {
    const [embedUrl, setEmbedUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        try {
            const embed = getEmbedUrl(url);
            setEmbedUrl(embed);
            if (!embed) {
                setError('Nie można przetworzyć podanego URL');
            }
        } catch (err) {
            setError('Wystąpił błąd podczas przetwarzania URL');
            console.error(err);
        }
    }, [url]);

    return { embedUrl, error };
};

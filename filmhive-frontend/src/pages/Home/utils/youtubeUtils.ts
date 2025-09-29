export function getYouTubeId(url?: string | null): string | null {
    // Sprawdź czy url istnieje i nie jest pusty
    if (!url || typeof url !== 'string') {
        return null;
    }

    const regExp = /^.*(?:youtu\.be\/|v\/|embed\/|watch\?v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[1].length === 11) ? match[1] : null;
}

export function getYouTubeThumbnail(videoId: string): string {
    return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
}

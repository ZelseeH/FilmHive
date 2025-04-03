// src/services/youtubeService.ts
export const getEmbedUrl = (youtubeUrl: string): string | null => {
    if (!youtubeUrl) return null;
    let videoId: string | null = null;

    try {
        const url = new URL(youtubeUrl);
        if (url.hostname.includes('youtube.com')) {
            if (url.pathname.startsWith('/watch')) {
                videoId = url.searchParams.get('v');
            } else if (url.pathname.startsWith('/embed/')) {
                videoId = url.pathname.split('/').pop() || null;
            }
        } else if (url.hostname === 'youtu.be') {
            videoId = url.pathname.slice(1);
        }
    } catch (error) {
        console.error('Invalid YouTube URL:', error);
        return null;
    }

    return videoId ? `https://www.youtube.com/embed/${videoId}` : null;
};

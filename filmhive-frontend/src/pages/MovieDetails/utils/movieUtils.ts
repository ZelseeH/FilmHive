
export const handleImageError = (
    e: React.SyntheticEvent<HTMLImageElement, Event>,
    fallbackSrc: string = '/placeholder-poster.jpg'
): void => {
    const target = e.target as HTMLImageElement;
    target.src = fallbackSrc;
    target.onerror = null;
};
export const formatReleaseYear = (releaseDate?: string): string => {
    if (!releaseDate) return '';
    return new Date(releaseDate).getFullYear().toString();
};

export const getYearFromDate = (dateString?: string): string => {
    if (!dateString) return '';
    return new Date(dateString).getFullYear().toString();
};

export const formatDirectorNames = (directors?: { name: string }[]): string => {
    if (!directors || directors.length === 0) return '';
    return directors.map(director => director.name).join(', ');
};

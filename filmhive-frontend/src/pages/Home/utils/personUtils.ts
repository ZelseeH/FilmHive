import { createSlug } from '../../../utils/formatters';

export const formatPersonName = (firstName?: string, lastName?: string): string => {
    if (!firstName && !lastName) return '';
    if (!firstName) return lastName || '';
    if (!lastName) return firstName;
    return `${firstName} ${lastName}`;
};

export const getPersonInitials = (name?: string): string => {
    if (!name) return '';
    return name
        .split(' ')
        .map(part => part.charAt(0))
        .join('')
        .toUpperCase();
};

export const formatPersonBirthDate = (birthDate?: string): string => {
    if (!birthDate) return '';
    return new Date(birthDate).toLocaleDateString();
};

export const calculateAge = (birthDate?: string, deathDate?: string): number | null => {
    if (!birthDate) return null;

    const birth = new Date(birthDate);
    const end = deathDate ? new Date(deathDate) : new Date();

    let age = end.getFullYear() - birth.getFullYear();
    const monthDiff = end.getMonth() - birth.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && end.getDate() < birth.getDate())) {
        age--;
    }

    return age;
};

export const formatPersonLifespan = (birthDate?: string, deathDate?: string): string => {
    if (!birthDate) return '';

    const birthYear = new Date(birthDate).getFullYear();
    const deathYear = deathDate ? new Date(deathDate).getFullYear() : null;

    return deathYear ? `${birthYear}-${deathYear}` : `ur. ${birthYear}`;
};

export const getPersonSlug = (name: string): string => {
    return createSlug(name);
};

export const handlePersonImageError = (
    e: React.SyntheticEvent<HTMLImageElement, Event>,
    type: 'actor' | 'director' = 'actor',
    fallbackSrc?: string
): void => {
    const target = e.target as HTMLImageElement;
    const defaultFallback = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3QgZmlsbD0iI2NjYyIgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiLz48L3N2Zz4=';
    target.src = fallbackSrc || defaultFallback;
    target.onerror = null;
};

export const formatFilmography = (movies?: { title: string; year?: string }[]): string => {
    if (!movies || movies.length === 0) return 'Brak informacji o filmografii';

    return movies
        .slice(0, 3)
        .map(movie => movie.year ? `${movie.title} (${movie.year})` : movie.title)
        .join(', ');
};

// Funkcja pomocnicza do określania typu osoby w tekście
export const getPersonTypeLabel = (type: 'actor' | 'director'): string => {
    return type === 'actor' ? 'Aktor' : 'Reżyser';
};

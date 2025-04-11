import { createSlug } from '../../../utils/formatters';

export const formatActorName = (firstName?: string, lastName?: string): string => {
    if (!firstName && !lastName) return '';
    if (!firstName) return lastName || '';
    if (!lastName) return firstName;
    return `${firstName} ${lastName}`;
};

export const getActorInitials = (name?: string): string => {
    if (!name) return '';
    return name
        .split(' ')
        .map(part => part.charAt(0))
        .join('')
        .toUpperCase();
};

export const formatActorBirthDate = (birthDate?: string): string => {
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

export const formatActorLifespan = (birthDate?: string, deathDate?: string): string => {
    if (!birthDate) return '';

    const birthYear = new Date(birthDate).getFullYear();
    const deathYear = deathDate ? new Date(deathDate).getFullYear() : null;

    return deathYear ? `${birthYear}-${deathYear}` : `ur. ${birthYear}`;
};

export const getActorSlug = (name: string): string => {
    return createSlug(name);
};

export const handleActorImageError = (
    e: React.SyntheticEvent<HTMLImageElement, Event>,
    fallbackSrc: string = '/placeholder-actor.jpg'
): void => {
    const target = e.target as HTMLImageElement;
    target.src = fallbackSrc;
    target.onerror = null;
};

export const formatFilmography = (movies?: { title: string; year?: string }[]): string => {
    if (!movies || movies.length === 0) return 'Brak informacji o filmografii';

    return movies
        .slice(0, 3)
        .map(movie => movie.year ? `${movie.title} (${movie.year})` : movie.title)
        .join(', ');
};

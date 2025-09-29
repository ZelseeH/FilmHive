// src/features/people/utils/personUtils.ts
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
    return new Date(birthDate).toLocaleDateString('pl-PL');
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
    const defaultFallback = type === 'actor' ? '/placeholder-actor.jpg' : '/placeholder-director.jpg';
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

export const formatGender = (gender?: 'M' | 'K' | null): string => {
    if (!gender) return 'Nie określono';
    return gender === 'M' ? 'Mężczyzna' : 'Kobieta';
};

export const truncateText = (text: string, maxLength: number): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

export const getPersonTypeLabel = (type: 'actor' | 'director'): string => {
    return type === 'actor' ? 'Aktor' : 'Reżyser';
};

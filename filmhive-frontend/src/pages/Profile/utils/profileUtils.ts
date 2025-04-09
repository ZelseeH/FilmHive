// utils/profileUtils.ts
export const getInitial = (username?: string): string => {
    return username?.[0]?.toUpperCase() || '?';
};

export const formatDate = (dateString?: string): string => {
    if (!dateString) return '31 lipca 2020';

    try {
        return new Date(dateString).toLocaleDateString('pl-PL');
    } catch (error) {
        console.error('Błąd formatowania daty:', error);
        return '31 lipca 2020';
    }
};

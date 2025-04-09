// hooks/useCountries.ts
import { useState, useEffect } from 'react';
import MovieFilterService from '../services/MovieFilterService';

export const useCountries = () => {
    const [countries, setCountries] = useState<string[]>([]);
    const [isLoadingCountries, setIsLoadingCountries] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchCountries = async () => {
            try {
                setIsLoadingCountries(true);
                const countriesData = await MovieFilterService.getCountries();
                setCountries(countriesData);
            } catch (err) {
                console.error('Błąd podczas pobierania krajów:', err);
                setError('Nie udało się pobrać listy krajów');
                // Fallback do statycznej listy w przypadku błędu
                setCountries(['USA', 'Wielka Brytania', 'Francja', 'Niemcy', 'Japonia', 'Korea Południowa', 'Polska', 'Włochy', 'Hiszpania', 'Kanada']);
            } finally {
                setIsLoadingCountries(false);
            }
        };

        fetchCountries();
    }, []);

    return { countries, isLoadingCountries, error };
};

// src/pages/ActorList/hooks/useBirthplaces.ts
import { useState, useEffect } from 'react';
import ActorFilterService from '../services/ActorFilterService';

export const useBirthplaces = () => {
    const [countries, setCountries] = useState<string[]>([]);
    const [isLoadingCountries, setIsLoadingCountries] = useState<boolean>(true);

    useEffect(() => {
        const fetchBirthplaces = async () => {
            try {
                setIsLoadingCountries(true);
                const birthplaces = await ActorFilterService.getBirthplaces();
                setCountries(birthplaces);
            } catch (error) {
                console.error('Error fetching birthplaces:', error);
                // Fallback do statycznej listy w przypadku błędu
                setCountries(['Chiny', 'Francja', 'Japonia', 'Korea Południowa', 'Niemcy', 'Nowa Zelandia', 'Polska', 'USA', 'Wielka Brytania', 'Włochy']);
            } finally {
                setIsLoadingCountries(false);
            }
        };

        fetchBirthplaces();
    }, []);

    return { countries, isLoadingCountries };
};

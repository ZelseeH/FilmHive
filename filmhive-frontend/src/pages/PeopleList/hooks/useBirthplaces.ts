import { useState, useEffect } from 'react';
import PeopleFilterService from '../services/PeopleFilterService';

/**
 * Hook zwracający listę unikalnych miejsc urodzenia osób (aktorów i reżyserów)
 * do wykorzystania w filtrach
 */
export const useBirthplaces = () => {
    const [countries, setCountries] = useState<string[]>([]);
    const [isLoadingCountries, setIsLoadingCountries] = useState<boolean>(true);

    useEffect(() => {
        const fetchBirthplaces = async () => {
            try {
                setIsLoadingCountries(true);
                const birthplaces = await PeopleFilterService.getBirthplaces();
                setCountries(birthplaces);
            } catch (error) {
                console.error('Error fetching birthplaces for people:', error);
                setCountries(['Chiny', 'Francja', 'Japonia', 'Korea Południowa', 'Niemcy', 'Nowa Zelandia', 'Polska', 'USA', 'Wielka Brytania', 'Włochy']);
            } finally {
                setIsLoadingCountries(false);
            }
        };

        fetchBirthplaces();
    }, []);

    return { countries, isLoadingCountries };
};

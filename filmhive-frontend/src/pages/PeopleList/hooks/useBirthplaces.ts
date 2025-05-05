import { useState, useEffect } from 'react';
import PeopleFilterService from '../services/PeopleFilterService';

export const useBirthplaces = (personType: 'actor' | 'director' = 'actor') => {
    const [countries, setCountries] = useState<string[]>([]);
    const [isLoadingCountries, setIsLoadingCountries] = useState<boolean>(true);

    useEffect(() => {
        const fetchBirthplaces = async () => {
            try {
                setIsLoadingCountries(true);
                const birthplaces = await PeopleFilterService.getBirthplaces(personType);
                setCountries(birthplaces);
            } catch (error) {
                console.error('Error fetching birthplaces:', error);
                // Fallback dla różnych typów osób
                const defaultCountries = {
                    actor: ['Chiny', 'Francja', 'Japonia', 'Korea Południowa', 'Niemcy', 'Nowa Zelandia', 'Polska', 'USA', 'Wielka Brytania', 'Włochy'],
                    director: ['USA', 'Wielka Brytania', 'Kanada', 'Francja', 'Niemcy', 'Polska', 'Włochy', 'Australia', 'Hiszpania', 'Japonia']
                };
                setCountries(defaultCountries[personType]);
            } finally {
                setIsLoadingCountries(false);
            }
        };

        fetchBirthplaces();
    }, [personType]);  // Dodano zależność od personType

    return { countries, isLoadingCountries };
};

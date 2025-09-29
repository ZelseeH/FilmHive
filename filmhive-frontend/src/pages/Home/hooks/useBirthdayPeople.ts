import { useState, useEffect, useCallback } from 'react';
import { Person, getPeopleWithBirthdayToday } from '../services/peopleService';

export const useBirthdayPeople = () => {
    const [people, setPeople] = useState<Person[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchBirthdayPeople = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await getPeopleWithBirthdayToday();
            setPeople(data);
        } catch (err: any) {
            setError(err.message || 'Błąd podczas pobierania osób z urodzinami');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchBirthdayPeople();
    }, [fetchBirthdayPeople]);

    return { people, loading, error };
};

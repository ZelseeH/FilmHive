import { useState, useEffect, useCallback } from 'react';
import { Person, getPersonById, getAllPeople } from '../services/peopleService';
import { getPersonSlug } from '../utils/personUtils';

interface UsePersonDetailsReturn {
    person: Person | null;
    loading: boolean;
    error: string | null;
}

export const usePersonDetails = (
    personId?: number,
    personSlug?: string,
    type: 'actor' | 'director' = 'actor'
): UsePersonDetailsReturn => {
    const [person, setPerson] = useState<Person | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchPersonDetails = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            if (personId) {
                const personData = await getPersonById(personId, type);
                setPerson(personData);
            } else if (personSlug) {
                const allPeopleResponse = await getAllPeople(1, 1000, type);
                const allPeople = allPeopleResponse.people;
                const foundPerson = allPeople.find(p => getPersonSlug(p.name) === personSlug);

                if (foundPerson) {
                    const personData = await getPersonById(foundPerson.id, foundPerson.type);
                    setPerson(personData);
                } else {
                    const typeLabel = type === 'actor' ? 'Aktor' : 'Reżyser';
                    setError(`${typeLabel} nie został znaleziony`);
                    setPerson(null);
                }
            } else {
                const typeLabel = type === 'actor' ? 'aktora' : 'reżysera';
                setError(`Brak identyfikatora ${typeLabel}`);
                setPerson(null);
            }
        } catch (err: any) {
            console.error('Błąd podczas pobierania danych osoby:', err);
            const typeLabel = type === 'actor' ? 'aktora' : 'reżysera';
            setError(err.message || `Wystąpił błąd podczas pobierania danych ${typeLabel}`);
            setPerson(null);
        } finally {
            setLoading(false);
        }
    }, [personId, personSlug, type]);

    useEffect(() => {
        fetchPersonDetails();
    }, [fetchPersonDetails]);

    return { person, loading, error };
};

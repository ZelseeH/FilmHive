// src/features/actors/hooks/useActorDetails.ts
import { useState, useEffect } from 'react';
import { Actor, getActorById, getAllActors } from '../services/actorService';
import { getActorSlug } from '../utils/actorUtils';

interface UseActorDetailsReturn {
    actor: Actor | null;
    loading: boolean;
    error: string | null;
}

export const useActorDetails = (actorId?: number, actorSlug?: string): UseActorDetailsReturn => {
    const [actor, setActor] = useState<Actor | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchActorDetails = async () => {
            try {
                setLoading(true);
                setError(null);

                if (actorId) {
                    const actorData = await getActorById(actorId);
                    setActor(actorData);
                } else if (actorSlug) {
                    const allActorsResponse = await getAllActors(1, 1000);
                    const allActors = allActorsResponse.actors;
                    const foundActor = allActors.find(a => getActorSlug(a.name) === actorSlug);

                    if (foundActor) {
                        const actorData = await getActorById(foundActor.id);
                        setActor(actorData);
                    } else {
                        setError('Aktor nie został znaleziony');
                    }
                } else {
                    setError('Brak identyfikatora aktora');
                }
            } catch (err: any) {
                console.error('Błąd podczas pobierania danych aktora:', err);
                setError(err.message || 'Wystąpił błąd podczas pobierania danych aktora');
            } finally {
                setLoading(false);
            }
        };

        fetchActorDetails();
    }, [actorId, actorSlug]);

    return { actor, loading, error };
};

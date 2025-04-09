// hooks/useActors.ts
import { useState, useEffect, useCallback } from 'react';
import { Actor } from '../services/actorService';

interface PaginationData {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
}

interface ActorsResponse {
    actors: Actor[];
    pagination: PaginationData;
}

interface Filters {
    name?: string;
    countries?: string;
    years?: string;
    gender?: string;
}

export const useActors = (filters: Filters, page: number) => {
    const [actors, setActors] = useState<Actor[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);

    const fetchActors = useCallback(async () => {
        try {
            setLoading(true);
            const queryParams = new URLSearchParams({
                page: page.toString(),
                per_page: '10',
                ...filters
            });

            const response = await fetch(`http://localhost:5000/api/actors/filter?${queryParams}`);

            if (!response.ok) {
                throw new Error('Nie udało się pobrać aktorów');
            }

            const data: ActorsResponse = await response.json();
            console.log('API response:', data);

            setActors(data.actors || []);
            setTotalPages(data.pagination?.total_pages || 1);
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania danych');
        } finally {
            setLoading(false);
        }
    }, [filters, page]);

    useEffect(() => {
        fetchActors();
    }, [fetchActors]);

    return { actors, loading, error, totalPages };
};

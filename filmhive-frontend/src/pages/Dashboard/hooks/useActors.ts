// hooks/useActors.ts
import { useState, useEffect, useCallback } from 'react';
import { Actor, createActor, updateActor, deleteActor, uploadActorPhoto } from '../services/actorService';
import { useAuth } from '../../../contexts/AuthContext';

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

interface SortOption {
    field: string;
    order: 'asc' | 'desc';
}

export const useActors = (
    filters: Filters,
    page: number,
    sortOption: SortOption = { field: 'name', order: 'asc' }
) => {
    const [actors, setActors] = useState<Actor[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);
    const { isStaff } = useAuth();

    const fetchActors = useCallback(async () => {
        try {
            setLoading(true);
            const queryParams = new URLSearchParams();

            queryParams.append('page', page.toString());
            queryParams.append('per_page', '10');

            if (filters.name) queryParams.append('name', filters.name);
            if (filters.countries) queryParams.append('countries', filters.countries);
            if (filters.years) queryParams.append('years', filters.years);
            if (filters.gender) queryParams.append('gender', filters.gender);

            queryParams.append('sort_by', sortOption.field);
            queryParams.append('sort_order', sortOption.order);

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
    }, [filters, page, sortOption]);

    useEffect(() => {
        fetchActors();
    }, [fetchActors]);

    // Dodawanie aktora
    const addActor = async (actorData: FormData): Promise<Actor | null> => {
        if (!isStaff()) {
            setError('Brak uprawnień do dodawania aktorów');
            return null;
        }

        try {
            setLoading(true);
            const actor = await createActor(actorData);
            await fetchActors(); // Odśwież listę
            return actor;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas dodawania aktora');
            return null;
        } finally {
            setLoading(false);
        }
    };

    // Edytowanie aktora
    const editActor = async (id: number, actorData: FormData): Promise<Actor | null> => {
        if (!isStaff()) {
            setError('Brak uprawnień do edytowania aktorów');
            return null;
        }

        try {
            setLoading(true);
            const actor = await updateActor(id, actorData);
            await fetchActors(); // Odśwież listę
            return actor;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas edytowania aktora');
            return null;
        } finally {
            setLoading(false);
        }
    };

    // Usuwanie aktora
    const removeActor = async (id: number): Promise<boolean> => {
        if (!isStaff()) {
            setError('Brak uprawnień do usuwania aktorów');
            return false;
        }

        try {
            setLoading(true);
            await deleteActor(id);
            await fetchActors(); // Odśwież listę
            return true;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas usuwania aktora');
            return false;
        } finally {
            setLoading(false);
        }
    };

    // Przesyłanie zdjęcia aktora
    const uploadPhoto = async (id: number, photoFile: File): Promise<Actor | null> => {
        if (!isStaff()) {
            setError('Brak uprawnień do przesyłania zdjęć');
            return null;
        }

        try {
            setLoading(true);
            const actor = await uploadActorPhoto(id, photoFile);
            await fetchActors(); // Odśwież listę
            return actor;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas przesyłania zdjęcia');
            return null;
        } finally {
            setLoading(false);
        }
    };

    return {
        actors,
        loading,
        error,
        totalPages,
        addActor,
        editActor,
        removeActor,
        uploadPhoto,
        refreshActors: fetchActors
    };
};

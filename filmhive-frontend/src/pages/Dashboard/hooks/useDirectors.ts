import { useState, useEffect, useCallback } from 'react';
import { Director, getDirectors, getDirectorById, searchDirectors, createDirector, updateDirector, deleteDirector, uploadDirectorPhoto } from '../services/directorService';
import { useAuth } from '../../../contexts/AuthContext';

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

export const useDirectors = (
    filters: Filters,
    page: number,
    sortOption: SortOption = { field: 'name', order: 'asc' }
) => {
    const [directors, setDirectors] = useState<Director[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);
    const { isStaff } = useAuth();

    const fetchDirectors = useCallback(async () => {
        try {
            setLoading(true);

            // Zamiast używać nieistniejącego endpointu /filter, używamy podstawowego endpointu
            // z parametrem name jeśli jest dostępny
            let url = `http://localhost:5000/api/directors/?page=${page}&per_page=10`;

            // Jeśli mamy filtr nazwy, użyj endpointu search
            if (filters.name) {
                url = `http://localhost:5000/api/directors/search?q=${encodeURIComponent(filters.name)}&page=${page}&per_page=10`;
            }

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error('Nie udało się pobrać reżyserów');
            }

            const data = await response.json();
            console.log('API response:', data);

            setDirectors(data.directors || []);
            setTotalPages(data.pagination?.total_pages || 1);
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania danych');
        } finally {
            setLoading(false);
        }
    }, [filters.name, page]);

    useEffect(() => {
        fetchDirectors();
    }, [fetchDirectors]);

    // Dodawanie reżysera
    const addDirector = async (directorData: FormData): Promise<Director | null> => {
        if (!isStaff()) {
            setError('Brak uprawnień do dodawania reżyserów');
            return null;
        }

        try {
            setLoading(true);
            const director = await createDirector(directorData);
            await fetchDirectors(); // Odśwież listę
            return director;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas dodawania reżysera');
            return null;
        } finally {
            setLoading(false);
        }
    };

    // Edytowanie reżysera
    const editDirector = async (id: number, directorData: FormData): Promise<Director | null> => {
        if (!isStaff()) {
            setError('Brak uprawnień do edytowania reżyserów');
            return null;
        }

        try {
            setLoading(true);
            const director = await updateDirector(id, directorData);
            await fetchDirectors(); // Odśwież listę
            return director;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas edytowania reżysera');
            return null;
        } finally {
            setLoading(false);
        }
    };

    // Usuwanie reżysera
    const removeDirector = async (id: number): Promise<boolean> => {
        if (!isStaff()) {
            setError('Brak uprawnień do usuwania reżyserów');
            return false;
        }

        try {
            setLoading(true);
            await deleteDirector(id);
            await fetchDirectors(); // Odśwież listę
            return true;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas usuwania reżysera');
            return false;
        } finally {
            setLoading(false);
        }
    };

    // Przesyłanie zdjęcia reżysera
    const uploadPhoto = async (id: number, photoFile: File): Promise<Director | null> => {
        if (!isStaff()) {
            setError('Brak uprawnień do przesyłania zdjęć');
            return null;
        }

        try {
            setLoading(true);
            const director = await uploadDirectorPhoto(id, photoFile);
            await fetchDirectors(); // Odśwież listę
            return director;
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas przesyłania zdjęcia');
            return null;
        } finally {
            setLoading(false);
        }
    };

    return {
        directors,
        loading,
        error,
        totalPages,
        addDirector,
        editDirector,
        removeDirector,
        uploadPhoto,
        refreshDirectors: fetchDirectors
    };
};

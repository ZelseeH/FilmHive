// hooks/usePeople.ts
import { useState, useEffect, useCallback } from 'react';

interface Person {
    id: number;
    name: string;
    birth_date?: string;
    birth_place?: string;
    biography?: string;
    photo_url?: string;
    gender?: string;
    type: 'actor' | 'director';
    movies?: { id: number; title: string }[];
}

interface PaginationData {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
}

interface PeopleResponse {
    data: Person[];
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

export const usePeople = (
    personType: 'actor' | 'director',
    filters: Filters,
    page: number,
    sortOption: SortOption = { field: 'name', order: 'asc' }
) => {
    const [people, setPeople] = useState<Person[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);

    const fetchPeople = useCallback(async () => {
        try {
            setLoading(true);
            const queryParams = new URLSearchParams({
                type: personType,
                page: page.toString(),
                per_page: '10',
                ...filters,
                sort_by: sortOption.field,
                sort_order: sortOption.order
            });

            const response = await fetch(`http://localhost:5000/api/people/filter?${queryParams}`);

            if (!response.ok) {
                throw new Error('Nie udało się pobrać danych');
            }

            const data: PeopleResponse = await response.json();

            setPeople(data.data || []);
            setTotalPages(data.pagination?.total_pages || 1);
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania danych');
            const defaultData = {
                actor: [],
                director: []
            };
            setPeople(defaultData[personType]);

        } finally {
            setLoading(false);
        }
    }, [personType, filters, page, sortOption]);

    useEffect(() => {
        fetchPeople();
    }, [fetchPeople]);

    return { people, loading, error, totalPages };
};

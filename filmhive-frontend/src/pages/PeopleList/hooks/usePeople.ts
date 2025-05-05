// hooks/usePeople.ts
import { useState, useEffect, useCallback } from 'react';
import { Person } from '../services/peopleService';

interface PaginationData {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
}

interface PeopleResponse {
    people: Person[];
    pagination: PaginationData;
}

interface Filters {
    name?: string;
    countries?: string;
    years?: string;
    gender?: string;
    type?: 'actor' | 'director';
}

interface SortOption {
    field: string;
    order: 'asc' | 'desc';
}

export const usePeople = (
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
            const queryParams = new URLSearchParams();

            queryParams.append('page', page.toString());
            queryParams.append('per_page', '10');

            if (filters.name) queryParams.append('name', filters.name);
            if (filters.countries) queryParams.append('countries', filters.countries);
            if (filters.years) queryParams.append('years', filters.years);
            if (filters.gender) queryParams.append('gender', filters.gender);
            if (filters.type) queryParams.append('type', filters.type);

            queryParams.append('sort_by', sortOption.field);
            queryParams.append('sort_order', sortOption.order);

            const response = await fetch(`http://localhost:5000/api/people/filter?${queryParams}`);

            if (!response.ok) {
                throw new Error('Nie udało się pobrać osób');
            }

            const data: PeopleResponse = await response.json();
            console.log('API response:', data);

            setPeople(data.people || []);
            setTotalPages(data.pagination?.total_pages || 1);
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania danych');
        } finally {
            setLoading(false);
        }
    }, [filters, page, sortOption]);

    useEffect(() => {
        fetchPeople();
    }, [fetchPeople]);

    return { people, loading, error, totalPages };
};

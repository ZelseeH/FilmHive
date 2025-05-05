import { useState, useCallback } from 'react';
import * as genresService from '../services/genresService';

export interface Genre {
    id: number;
    name: string;
}

export function useGenres(token: string) {
    const [genres, setGenres] = useState<Genre[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadGenres = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await genresService.fetchGenres(token);
            setGenres(data);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [token]);

    const add = useCallback(async (name: string) => {
        setLoading(true);
        setError(null);
        try {
            const newGenre = await genresService.addGenre(token, name);
            setGenres((prev) => [...prev, newGenre]);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [token]);

    const update = useCallback(async (id: number, name: string) => {
        setLoading(true);
        setError(null);
        try {
            const updated = await genresService.updateGenre(token, id, name);
            setGenres((prev) => prev.map(g => g.id === id ? updated : g));
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [token]);

    const remove = useCallback(async (id: number) => {
        setLoading(true);
        setError(null);
        try {
            await genresService.deleteGenre(token, id);
            setGenres((prev) => prev.filter(g => g.id !== id));
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [token]);

    return { genres, loading, error, loadGenres, add, update, remove };
}

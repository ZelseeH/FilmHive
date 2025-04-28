// src/hooks/useSearchResults.ts
import { useEffect, useState } from "react";
import { searchMovies, searchActors, searchUsers } from "../services/searchService";

export type Tab = "movies" | "actors" | "users";

export function useSearchResults(query: string, tab: Tab, page: number) {
    const [loading, setLoading] = useState(false);
    const [movies, setMovies] = useState<any[]>([]);
    const [actors, setActors] = useState<any[]>([]);
    const [users, setUsers] = useState<any[]>([]);
    const [movieCount, setMovieCount] = useState(0);
    const [actorCount, setActorCount] = useState(0);
    const [userCount, setUserCount] = useState(0);
    const [moviePages, setMoviePages] = useState(1);
    const [actorPages, setActorPages] = useState(1);
    const [userPages, setUserPages] = useState(1);

    useEffect(() => {
        if (!query) return;
        Promise.all([
            searchMovies(query, 1),
            searchActors(query, 1),
            searchUsers(query, 1),
        ]).then(([movieData, actorData, userData]) => {
            setMovieCount(movieData.pagination?.total || 0);
            setActorCount(actorData.pagination?.total || 0);
            setUserCount(userData.pagination?.total || 0);
            setMoviePages(movieData.pagination?.total_pages || 1);
            setActorPages(actorData.pagination?.total_pages || 1);
            setUserPages(userData.pagination?.total_pages || 1);
        });
    }, [query]);

    useEffect(() => {
        if (!query) return;
        setLoading(true);
        if (tab === "movies") {
            searchMovies(query, page).then(movieData => {
                setMovies(movieData.movies || movieData.results || []);
            }).finally(() => setLoading(false));
        } else if (tab === "actors") {
            searchActors(query, page).then(actorData => {
                setActors(actorData.actors || actorData.results || []);
            }).finally(() => setLoading(false));
        } else if (tab === "users") {
            searchUsers(query, page).then(userData => {
                setUsers(userData.users || userData.results || []);
            }).finally(() => setLoading(false));
        }
    }, [query, tab, page]);

    return {
        loading,
        movies, actors, users,
        movieCount, actorCount, userCount,
        moviePages, actorPages, userPages
    };
}

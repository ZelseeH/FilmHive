// src/hooks/useSearchResults.ts
import { useEffect, useState } from "react";
import { searchMovies, searchPeople, searchUsers } from "../services/searchService";

export type Tab = "movies" | "people" | "users";

export function useSearchResults(query: string, tab: Tab, page: number) {
    const [loading, setLoading] = useState(false);
    const [movies, setMovies] = useState<any[]>([]);
    const [people, setPeople] = useState<any[]>([]);
    const [users, setUsers] = useState<any[]>([]);
    const [movieCount, setMovieCount] = useState(0);
    const [peopleCount, setPeopleCount] = useState(0);
    const [userCount, setUserCount] = useState(0);
    const [moviePages, setMoviePages] = useState(1);
    const [peoplePages, setPeoplePages] = useState(1);
    const [userPages, setUserPages] = useState(1);

    useEffect(() => {
        if (!query) return;
        Promise.all([
            searchMovies(query, 1),
            searchPeople(query, 1),
            searchUsers(query, 1),
        ]).then(([movieData, peopleData, userData]) => {
            setMovieCount(movieData.pagination?.total || 0);
            setPeopleCount(peopleData.pagination?.total || 0);
            setUserCount(userData.pagination?.total || 0);
            setMoviePages(movieData.pagination?.total_pages || 1);
            setPeoplePages(peopleData.pagination?.total_pages || 1);
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
        } else if (tab === "people") {
            searchPeople(query, page).then(peopleData => {
                setPeople(peopleData.people || peopleData.results || []);
            }).finally(() => setLoading(false));
        } else if (tab === "users") {
            searchUsers(query, page).then(userData => {
                setUsers(userData.users || userData.results || []);
            }).finally(() => setLoading(false));
        }
    }, [query, tab, page]);

    return {
        loading,
        movies, people, users,
        movieCount, peopleCount, userCount,
        moviePages, peoplePages, userPages
    };
}

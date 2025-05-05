import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { FaSearch } from "react-icons/fa";
import { useSearchResults, Tab } from "./hooks/useSearchResults";
import MovieItem from '../../pages/MovieList/components/MovieItem/MovieItem';
import PersonItem from '../../pages/PeopleList/components/PeopleItem';
import UserItem from './components/UserItem/UserItem';
import Pagination from '../../components/ui/Pagination';
import styles from './SearchPage.module.css';

const SearchPage: React.FC = () => {
    const [searchParams] = useSearchParams();
    const query = searchParams.get("query") || "";
    const [search, setSearch] = useState("");  // Inicjalizujemy jako pusty ciąg
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<Tab>("movies");
    const [moviePage, setMoviePage] = useState(1);
    const [peoplePage, setPeoplePage] = useState(1);
    const [userPage, setUserPage] = useState(1);

    const currentPage =
        activeTab === "movies" ? moviePage :
            activeTab === "people" ? peoplePage :
                userPage;

    const {
        loading,
        movies, people, users,
        movieCount, peopleCount, userCount,
        moviePages, peoplePages, userPages
    } = useSearchResults(query, activeTab, currentPage);

    useEffect(() => {
        setMoviePage(1);
        setPeoplePage(1);
        setUserPage(1);
    }, [query, activeTab]);

    // Usunięto efekt, który ustawiał wartość pola wyszukiwania na podstawie query

    const handleSubmit = (e?: React.FormEvent | React.MouseEvent) => {
        if (e) e.preventDefault();
        if (search.trim()) {
            navigate(`/search?query=${encodeURIComponent(search.trim())}`);
            setSearch(""); // Czyszczenie pola wyszukiwania po wysłaniu
        }
    };

    return (
        <div className={styles.pageWrapper}>
            <div className={styles.container}>
                <div className={styles.searchFormContainer}>
                    <form className={styles.searchForm} onSubmit={handleSubmit} role="search" autoComplete="off">
                        <input
                            type="text"
                            className={styles.searchInput}
                            placeholder="Szukaj filmów, osób, użytkowników..."
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            aria-label="Szukaj"
                        />
                        <button
                            type="submit"
                            className={styles.searchButton}
                            aria-label="Szukaj"
                        >
                            <FaSearch />
                        </button>
                    </form>
                </div>

                <h2 className={styles.pageTitle}>
                    Wyniki wyszukiwania dla: <span className={styles.query}>{query}</span>
                </h2>
                <div className={styles.tabsBar}>
                    <button
                        className={`${styles.tabButton} ${activeTab === "movies" ? styles.active : ""}`}
                        onClick={() => setActiveTab("movies")}
                    >
                        Filmy <span className={styles.tabCount}>({movieCount})</span>
                    </button>
                    <button
                        className={`${styles.tabButton} ${activeTab === "people" ? styles.active : ""}`}
                        onClick={() => setActiveTab("people")}
                    >
                        Osoby <span className={styles.tabCount}>({peopleCount})</span>
                    </button>
                    <button
                        className={`${styles.tabButton} ${activeTab === "users" ? styles.active : ""}`}
                        onClick={() => setActiveTab("users")}
                    >
                        Użytkownicy <span className={styles.tabCount}>({userCount})</span>
                    </button>
                </div>

                <div className={styles.resultsSection}>
                    {loading && <div className={styles.loading}>Ładowanie wyników...</div>}

                    {!loading && activeTab === "movies" && (
                        <>
                            {movies.length === 0 ? (
                                <div className={styles.noResults}>Brak filmów pasujących do wyszukiwania.</div>
                            ) : (
                                movies.map(movie => (
                                    <MovieItem key={movie.id || movie.movie_id} movie={movie} />
                                ))

                            )}
                            {moviePages > 1 && (
                                <Pagination
                                    currentPage={moviePage}
                                    totalPages={moviePages}
                                    onPageChange={setMoviePage}
                                />
                            )}
                        </>
                    )}

                    {!loading && activeTab === "people" && (
                        <>
                            {people.length === 0 ? (
                                <div className={styles.noResults}>Brak osób pasujących do wyszukiwania.</div>
                            ) : (
                                people.map(person => (
                                    <PersonItem key={`${person.type}-${person.id}`} person={person} />
                                ))
                            )}
                            {peoplePages > 1 && (
                                <Pagination
                                    currentPage={peoplePage}
                                    totalPages={peoplePages}
                                    onPageChange={setPeoplePage}
                                />
                            )}
                        </>
                    )}

                    {!loading && activeTab === "users" && (
                        <>
                            {users.length === 0 ? (
                                <div className={styles.noResults}>Brak użytkowników pasujących do wyszukiwania.</div>
                            ) : (
                                users.map(user => (
                                    <UserItem key={user.id} user={user} />
                                ))
                            )}
                            {userPages > 1 && (
                                <Pagination
                                    currentPage={userPage}
                                    totalPages={userPages}
                                    onPageChange={setUserPage}
                                />
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SearchPage;

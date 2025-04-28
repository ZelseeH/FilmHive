import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useSearchResults, Tab } from "./hooks/useSearchResults";
import MovieItem from '../../pages/MovieList/components/MovieItem/MovieItem';
import ActorItem from '../../pages/ActorList/components/ActorItem';
import UserItem from './components/UserItem/UserItem';
import Pagination from '../../components/ui/Pagination';
import styles from './SearchPage.module.css';

const SearchPage: React.FC = () => {
    const [searchParams] = useSearchParams();
    const query = searchParams.get("query") || "";
    const [activeTab, setActiveTab] = useState<Tab>("movies");
    const [moviePage, setMoviePage] = useState(1);
    const [actorPage, setActorPage] = useState(1);
    const [userPage, setUserPage] = useState(1);

    const currentPage =
        activeTab === "movies" ? moviePage :
            activeTab === "actors" ? actorPage :
                userPage;

    const {
        loading,
        movies, actors, users,
        movieCount, actorCount, userCount,
        moviePages, actorPages, userPages
    } = useSearchResults(query, activeTab, currentPage);

    useEffect(() => {
        setMoviePage(1);
        setActorPage(1);
        setUserPage(1);
    }, [query, activeTab]);

    return (
        <div className={styles.pageWrapper}>
            <div className={styles.container}>
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
                        className={`${styles.tabButton} ${activeTab === "actors" ? styles.active : ""}`}
                        onClick={() => setActiveTab("actors")}
                    >
                        Aktorzy <span className={styles.tabCount}>({actorCount})</span>
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

                    {!loading && activeTab === "actors" && (
                        <>
                            {actors.length === 0 ? (
                                <div className={styles.noResults}>Brak aktorów pasujących do wyszukiwania.</div>
                            ) : (
                                actors.map(actor => (
                                    <ActorItem key={actor.id} actor={actor} />
                                ))
                            )}
                            {actorPages > 1 && (
                                <Pagination
                                    currentPage={actorPage}
                                    totalPages={actorPages}
                                    onPageChange={setActorPage}
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

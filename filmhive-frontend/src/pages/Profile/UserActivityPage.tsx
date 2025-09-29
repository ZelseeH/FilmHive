import React, { useState, useRef, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAllUserRatedMovies } from './hooks/useAllUserRatedMovies';
import { useAllUserFavoriteMovies } from './hooks/useAllUserFavoriteMovies';
import { useAllUserWatchlistMovies } from './hooks/useAllUserWatchlistMovies';
import { useProfileData } from './hooks/useProfileData';
import MovieCard from './components/MovieCard/MovieCard';
import { ConfirmDialog } from 'primereact/confirmdialog';
import { Toast, ToastMessage } from 'primereact/toast';
import { Paginator } from 'primereact/paginator'; // DODAJ
import styles from './UserActivityPage.module.css';

type ActivityTab = 'ratings' | 'favorites' | 'watchlist';

const ITEMS_PER_PAGE = 50; // Ilość filmów na stronę

const UserActivityPage: React.FC = () => {
    const { username } = useParams<{ username?: string }>();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<ActivityTab>('ratings');

    // DODAJ state dla paginacji
    const [currentPage, setCurrentPage] = useState(0); // PrimeReact używa 0-based indexing

    const toast = useRef<Toast>(null);

    const { profileData, loading: profileLoading, isOwnProfile } = useProfileData(username);

    const { movies: ratedMovies, loading: ratingsLoading, error: ratingsError } = useAllUserRatedMovies(username);
    const {
        movies: favoriteMovies,
        loading: favoritesLoading,
        error: favoritesError,
        removeFavorite
    } = useAllUserFavoriteMovies(username);
    const {
        movies: watchlistMovies,
        loading: watchlistLoading,
        error: watchlistError,
        removeFromWatchlist
    } = useAllUserWatchlistMovies(username);

    const showToast = (message: ToastMessage) => {
        toast.current?.show(message);
    };

    // DODAJ funkcję do zresetowania paginacji przy zmianie taba
    const handleTabChange = (tab: ActivityTab) => {
        setActiveTab(tab);
        setCurrentPage(0); // Reset do pierwszej strony
    };

    // DODAJ paginowane dane
    const paginatedData = useMemo(() => {
        let currentMovies: any[] = [];

        switch (activeTab) {
            case 'ratings':
                currentMovies = ratedMovies;
                break;
            case 'favorites':
                currentMovies = favoriteMovies;
                break;
            case 'watchlist':
                currentMovies = watchlistMovies;
                break;
        }

        const startIndex = currentPage * ITEMS_PER_PAGE;
        const endIndex = startIndex + ITEMS_PER_PAGE;

        return {
            items: currentMovies.slice(startIndex, endIndex),
            totalRecords: currentMovies.length,
            startIndex
        };
    }, [activeTab, currentPage, ratedMovies, favoriteMovies, watchlistMovies]);

    // Wrapper functions
    const handleRemoveFavorite = async (movieId: number): Promise<void> => {
        try {
            const success = await removeFavorite(movieId);
            if (!success) {
                throw new Error('Nie udało się usunąć filmu z ulubionych');
            }
        } catch (error) {
            console.error('Error removing favorite:', error);
            throw error;
        }
    };

    const handleRemoveFromWatchlist = async (movieId: number): Promise<void> => {
        try {
            const success = await removeFromWatchlist(movieId);
            if (!success) {
                throw new Error('Nie udało się usunąć filmu z listy do obejrzenia');
            }
        } catch (error) {
            console.error('Error removing from watchlist:', error);
            throw error;
        }
    };

    if (profileLoading) {
        return <div className={styles.loading}>Ładowanie...</div>;
    }

    if (!profileData) {
        return <div className={styles.error}>Nie znaleziono profilu</div>;
    }

    const getActiveContent = () => {
        switch (activeTab) {
            case 'ratings':
                if (ratingsLoading) return <div className={styles.loading}>Ładowanie ocen...</div>;
                if (ratingsError) return <div className={styles.error}>Błąd: {ratingsError}</div>;
                if (!ratedMovies.length) return <div className={styles.empty}>Brak ocenionych filmów</div>;

                return (
                    <div className={styles.contentWithPagination}>
                        <div className={styles.movieList}>
                            {paginatedData.items.map((movie, index) => (
                                <MovieCard
                                    key={movie.movie_id}
                                    movie={{
                                        id: movie.movie_id,
                                        title: movie.title,
                                        poster_url: movie.poster_url,
                                        user_rating: movie.rating,
                                        rated_at: movie.rated_at
                                    }}
                                    index={paginatedData.startIndex + index + 1} // POPRAW numerację
                                    type="ratings"
                                    isOwnProfile={isOwnProfile}
                                    showToast={showToast}
                                />
                            ))}
                        </div>

                        {/* DODAJ Paginator */}
                        {paginatedData.totalRecords > ITEMS_PER_PAGE && (
                            <div className={styles.paginationContainer}>
                                <Paginator
                                    first={currentPage * ITEMS_PER_PAGE}
                                    rows={ITEMS_PER_PAGE}
                                    totalRecords={paginatedData.totalRecords}
                                    onPageChange={(e) => setCurrentPage(e.page!)}
                                    template={{
                                        layout: 'PrevPageLink PageLinks NextPageLink CurrentPageReport',
                                        CurrentPageReport: (options: any) => (
                                            <span className={styles.pageInfo}>
                                                {options.first + 1}-{Math.min(options.last + 1, options.totalRecords)} z {options.totalRecords}
                                            </span>
                                        )
                                    }}
                                    pageLinkSize={5}
                                />
                            </div>
                        )}
                    </div>
                );

            case 'favorites':
                if (favoritesLoading) return <div className={styles.loading}>Ładowanie ulubionych...</div>;
                if (favoritesError) return <div className={styles.error}>Błąd: {favoritesError}</div>;
                if (!favoriteMovies.length) return <div className={styles.empty}>Brak ulubionych filmów</div>;

                return (
                    <div className={styles.contentWithPagination}>
                        <div className={styles.movieList}>
                            {paginatedData.items.map((movie, index) => (
                                <MovieCard
                                    key={movie.movie_id}
                                    movie={{
                                        id: movie.movie_id,
                                        title: movie.title,
                                        poster_url: movie.poster_url,
                                        added_at: movie.added_at
                                    }}
                                    index={paginatedData.startIndex + index + 1}
                                    type="favorites"
                                    onRemove={handleRemoveFavorite}
                                    isOwnProfile={isOwnProfile}
                                    showToast={showToast}
                                />
                            ))}
                        </div>

                        {paginatedData.totalRecords > ITEMS_PER_PAGE && (
                            <div className={styles.paginationContainer}>
                                <Paginator
                                    first={currentPage * ITEMS_PER_PAGE}
                                    rows={ITEMS_PER_PAGE}
                                    totalRecords={paginatedData.totalRecords}
                                    onPageChange={(e) => setCurrentPage(e.page!)}
                                    template={{
                                        layout: 'PrevPageLink PageLinks NextPageLink CurrentPageReport',
                                        CurrentPageReport: (options: any) => (
                                            <span className={styles.pageInfo}>
                                                {options.first + 1}-{Math.min(options.last + 1, options.totalRecords)} z {options.totalRecords}
                                            </span>
                                        )
                                    }}
                                    pageLinkSize={5}
                                />
                            </div>
                        )}
                    </div>
                );

            case 'watchlist':
                if (watchlistLoading) return <div className={styles.loading}>Ładowanie listy...</div>;
                if (watchlistError) return <div className={styles.error}>Błąd: {watchlistError}</div>;
                if (!watchlistMovies.length) return <div className={styles.empty}>Lista jest pusta</div>;

                return (
                    <div className={styles.contentWithPagination}>
                        <div className={styles.movieList}>
                            {paginatedData.items.map((movie, index) => (
                                <MovieCard
                                    key={movie.movie_id}
                                    movie={{
                                        id: movie.movie_id,
                                        title: movie.title,
                                        poster_url: movie.poster_url,
                                        added_at: movie.added_at
                                    }}
                                    index={paginatedData.startIndex + index + 1}
                                    type="watchlist"
                                    onRemove={handleRemoveFromWatchlist}
                                    isOwnProfile={isOwnProfile}
                                    showToast={showToast}
                                />
                            ))}
                        </div>

                        {paginatedData.totalRecords > ITEMS_PER_PAGE && (
                            <div className={styles.paginationContainer}>
                                <Paginator
                                    first={currentPage * ITEMS_PER_PAGE}
                                    rows={ITEMS_PER_PAGE}
                                    totalRecords={paginatedData.totalRecords}
                                    onPageChange={(e) => setCurrentPage(e.page!)}
                                    template={{
                                        layout: 'PrevPageLink PageLinks NextPageLink CurrentPageReport',
                                        CurrentPageReport: (options: any) => (
                                            <span className={styles.pageInfo}>
                                                {options.first + 1}-{Math.min(options.last + 1, options.totalRecords)} z {options.totalRecords}
                                            </span>
                                        )
                                    }}
                                    pageLinkSize={5}
                                />
                            </div>
                        )}
                    </div>
                );

            default:
                return null;
        }
    };

    const getTabTitle = (tab: ActivityTab) => {
        switch (tab) {
            case 'ratings':
                return `Oceny (${ratedMovies.length})`;
            case 'favorites':
                return `Ulubione (${favoriteMovies.length})`;
            case 'watchlist':
                return `Do obejrzenia (${watchlistMovies.length})`;
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <button
                    className={styles.backButton}
                    onClick={() => navigate(`/profile/${username}`)}
                >
                    ← Powrót do profilu
                </button>
                <h1>Aktywność użytkownika {profileData.username}</h1>
            </div>

            <div className={styles.tabs}>
                {(['ratings', 'favorites', 'watchlist'] as ActivityTab[]).map(tab => (
                    <button
                        key={tab}
                        className={`${styles.tab} ${activeTab === tab ? styles.active : ''}`}
                        onClick={() => handleTabChange(tab)}
                    >
                        {getTabTitle(tab)}
                    </button>
                ))}
            </div>

            <div className={styles.content}>
                {getActiveContent()}
            </div>

            <Toast ref={toast} position="top-right" />
            <ConfirmDialog />
        </div>
    );
};

export default UserActivityPage;

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { getMovieById, deleteMovie } from '../../services/movieService';
import { getMovieActors } from '../../services/movieRelationsService';
import { useMovieRelations } from '../../hooks/useMovieRelations';
import styles from './MoviesAddPartTwo.module.css';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Toast } from 'primereact/toast';
import ActorsSection from './ActorsSection';
import DirectorsSection from './DirectorsSection';
import GenresSection from './GenresSection';

interface MovieAddPartTwoParams {
    id: string;
}

const MoviesAddPartTwo: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { isStaff } = useAuth();
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [movieData, setMovieData] = useState<any>(null);
    const [saving, setSaving] = useState<boolean>(false);
    const toast = useRef<Toast>(null);

    // Pobieranie ID filmu z parametru URL
    const movieId = id ? parseInt(id) : undefined;

    useEffect(() => {
        if (movieId) {
            fetchMovieDetails(movieId);
        }
    }, [movieId]);

    const fetchMovieDetails = async (movieId: number) => {
        try {
            setLoading(true);
            const data = await getMovieById(movieId);

            // Pobierz aktorów z rolami osobno
            const actorsWithRoles = await getMovieActors(movieId);

            // Zastąp aktorów z głównego endpointu aktorami z rolami
            const movieWithRoles = {
                ...data,
                actors: actorsWithRoles
            };

            setMovieData(movieWithRoles);
            setError(null);
        } catch (err: any) {
            setError(err.message);
            console.error('Error fetching movie details:', err);
        } finally {
            setLoading(false);
        }
    };

    // Hook do zarządzania relacjami
    const {
        addActor,
        removeActor,
        addDirector,
        removeDirector,
        addGenre,
        removeGenre,
        loading: relationsLoading,
        error: relationsError
    } = useMovieRelations(movieId!);

    // FUNKCJE OBSŁUGI RELACJI
    const handleRemoveActor = async (actorId: number) => {
        const success = await removeActor(actorId);
        if (success) {
            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Aktor został usunięty z filmu',
                life: 3000
            });
            fetchMovieDetails(movieId!);
        }
    };

    const handleRemoveDirector = async (directorId: number) => {
        const success = await removeDirector(directorId);
        if (success) {
            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Reżyser został usunięty z filmu',
                life: 3000
            });
            fetchMovieDetails(movieId!);
        }
    };

    const handleRemoveGenre = async (genreId: number) => {
        const success = await removeGenre(genreId);
        if (success) {
            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Gatunek został usunięty z filmu',
                life: 3000
            });
            fetchMovieDetails(movieId!);
        }
    };

    const handleAddActors = async (actors: { actorId: number; role: string }[]): Promise<boolean> => {
        try {
            let allSuccess = true;
            for (const actorData of actors) {
                const success = await addActor(actorData.actorId, actorData.role);
                if (!success) {
                    allSuccess = false;
                    break;
                }
            }
            if (allSuccess) {
                fetchMovieDetails(movieId!);
            }
            return allSuccess;
        } catch (error) {
            console.error('Error adding actors:', error);
            return false;
        }
    };

    const handleAddDirectors = async (directorIds: number[]): Promise<boolean> => {
        try {
            let allSuccess = true;
            for (const directorId of directorIds) {
                const success = await addDirector(directorId);
                if (!success) {
                    allSuccess = false;
                    break;
                }
            }
            if (allSuccess) {
                fetchMovieDetails(movieId!);
            }
            return allSuccess;
        } catch (error) {
            console.error('Error adding directors:', error);
            return false;
        }
    };

    const handleAddGenres = async (genreIds: number[]): Promise<boolean> => {
        try {
            let allSuccess = true;
            for (const genreId of genreIds) {
                const success = await addGenre(genreId);
                if (!success) {
                    allSuccess = false;
                    break;
                }
            }
            if (allSuccess) {
                fetchMovieDetails(movieId!);
            }
            return allSuccess;
        } catch (error) {
            console.error('Error adding genres:', error);
            return false;
        }
    };

    // FINALIZACJA FILMU
    const handleFinishMovie = async () => {
        setSaving(true);

        try {
            // Film już istnieje z relacjami - po prostu przekieruj
            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Film został pomyślnie dodany do bazy danych!',
                life: 3000
            });

            // Przekieruj do listy filmów po krótkim opóźnieniu
            setTimeout(() => {
                navigate('/dashboardpanel/movies/manage');
            }, 1500);
        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Wystąpił błąd podczas finalizacji filmu',
                life: 5000
            });
        } finally {
            setSaving(false);
        }
    };

    // ANULOWANIE - USUŃ FILM
    const handleCancelAddMovie = () => {
        confirmDialog({
            message: `Czy na pewno chcesz anulować dodawanie filmu "${movieData?.title}"? Film zostanie całkowicie usunięty z bazy danych.`,
            header: 'Potwierdzenie anulowania',
            icon: 'pi pi-exclamation-triangle',
            acceptClassName: 'p-button-danger',
            accept: confirmDeleteMovie,
            reject: () => { }
        });
    };

    const confirmDeleteMovie = async () => {
        try {
            setSaving(true);
            await deleteMovie(movieId!);

            toast.current?.show({
                severity: 'info',
                summary: 'Anulowano',
                detail: 'Film został usunięty z bazy danych',
                life: 3000
            });

            // Przekieruj do listy filmów
            setTimeout(() => {
                navigate('/dashboardpanel/movies/manage');
            }, 1500);
        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się usunąć filmu',
                life: 5000
            });
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p>Ładowanie danych filmu...</p>
            </div>
        );
    }

    if (error || !movieData) {
        return <div className={styles.errorMessage}>Nie można załadować danych filmu</div>;
    }

    const formatDate = (dateString?: string): string => {
        if (!dateString) return '';
        return dateString.split('T')[0];
    };

    return (
        <div className={styles.container}>
            <Toast ref={toast} />
            <ConfirmDialog />

            <div className={styles.header}>
                <h1 className={styles.title}>
                    Dodaj nowy film - Krok 2/2
                </h1>
                <div className={styles.subtitle}>
                    Dodaj aktorów, reżyserów i gatunki do filmu
                </div>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}
            {relationsError && <div className={styles.errorMessage}>{relationsError}</div>}

            <div className={styles.movieCard}>
                <div className={styles.movieHeader}>
                    <div className={styles.movieInfo}>
                        {movieData.poster_url ? (
                            <img src={movieData.poster_url} alt={movieData.title} className={styles.moviePoster} />
                        ) : (
                            <div className={styles.moviePosterPlaceholder}>
                                {movieData.title.charAt(0).toUpperCase()}
                            </div>
                        )}
                        <div className={styles.movieDetails}>
                            <h2>{movieData.title}</h2>
                            <p className={styles.movieMeta}>
                                {movieData.release_date && formatDate(movieData.release_date)} •
                                {movieData.duration_minutes && ` ${movieData.duration_minutes} min`} •
                                {movieData.country}
                            </p>
                            {movieData.description && (
                                <p className={styles.movieDescription}>{movieData.description}</p>
                            )}
                        </div>
                    </div>
                </div>

                <div className={styles.relationsContent}>
                    <div className={styles.progressInfo}>
                        <h3>Dodaj relacje do filmu</h3>
                        <p>Film został utworzony w bazie danych. Teraz możesz dodać aktorów, reżyserów i gatunki.</p>
                    </div>

                    {/* SEKCJE RELACJI */}
                    <ActorsSection
                        actors={movieData.actors || []}
                        onRemoveActor={handleRemoveActor}
                        onAddActors={handleAddActors}
                        relationsLoading={relationsLoading}
                    />

                    <DirectorsSection
                        directors={movieData.directors || []}
                        onRemoveDirector={handleRemoveDirector}
                        onAddDirectors={handleAddDirectors}
                        relationsLoading={relationsLoading}
                    />

                    <GenresSection
                        genres={movieData.genres || []}
                        onRemoveGenre={handleRemoveGenre}
                        onAddGenres={handleAddGenres}
                        relationsLoading={relationsLoading}
                    />
                </div>

                <div className={styles.actionsFooter}>
                    <button
                        className={styles.cancelButton}
                        onClick={handleCancelAddMovie}
                        disabled={saving}
                    >
                        {saving ? 'Anulowanie...' : 'Anuluj i usuń film'}
                    </button>
                    <button
                        className={styles.finishButton}
                        onClick={handleFinishMovie}
                        disabled={saving}
                    >
                        {saving ? 'Zapisywanie...' : 'Dodaj film do bazy'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MoviesAddPartTwo;

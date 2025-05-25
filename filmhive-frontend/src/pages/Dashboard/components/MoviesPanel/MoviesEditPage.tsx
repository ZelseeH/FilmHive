import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { getMovieById, updateMovie, deleteMovie, uploadMoviePoster } from '../../services/movieService';
import { getMovieActors } from '../../services/movieRelationsService';
import { useMovieRelations } from '../../hooks/useMovieRelations';
import { useInlineEdit } from '../../hooks/useInlineEdit';
import styles from './MoviesEditPage.module.css';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Toast } from 'primereact/toast';
import ActorsSection from './ActorsSection';
import DirectorsSection from './DirectorsSection';
import GenresSection from './GenresSection';

interface MovieEditParams {
    id: string;
}

const MoviesEditPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { getToken, isStaff } = useAuth();
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [movieData, setMovieData] = useState<any>(null);

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

    // Jeśli dane filmu nie są jeszcze załadowane, nie inicjalizuj hooka
    if (!movieData && !loading) {
        return <div className={styles.errorMessage}>Nie można załadować danych filmu</div>;
    }

    if (loading) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p>Ładowanie danych filmu...</p>
            </div>
        );
    }

    return (
        <MovieEditContent
            movieData={movieData}
            movieId={movieId as number}
            error={error}
            onRefresh={() => fetchMovieDetails(movieId as number)}
            navigate={navigate}
        />
    );
};

interface MovieEditContentProps {
    movieData: any;
    movieId: number;
    error: string | null;
    onRefresh: () => void;
    navigate: any;
}

const MovieEditContent: React.FC<MovieEditContentProps> = ({
    movieData,
    movieId,
    error,
    onRefresh,
    navigate
}) => {
    const { fields, toggleEdit, updateField, cancelEdit, getValues, setInputRef } = useInlineEdit(movieData);
    const [saveLoading, setSaveLoading] = useState<Record<string, boolean>>({});
    const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
    const [posterFile, setPosterFile] = useState<File | null>(null);
    const [posterPreview, setPosterPreview] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const toast = useRef<Toast>(null);

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
    } = useMovieRelations(movieId);

    const handleFieldSave = async (fieldName: string) => {
        try {
            // Walidacja pól przed zapisem
            let isValid = true;
            let errorMessage = '';

            if (fieldName === 'title') {
                const value = fields[fieldName].value;
                if (!value || !value.trim()) {
                    isValid = false;
                    errorMessage = 'Tytuł jest wymagany';
                } else if (value.length > 200) {
                    isValid = false;
                    errorMessage = 'Tytuł nie może być dłuższy niż 200 znaków';
                }
            } else if (fieldName === 'release_date') {
                const value = fields[fieldName].value;
                if (value) {
                    const selectedDate = new Date(value);
                    const today = new Date();
                    if (selectedDate > today) {
                        isValid = false;
                        errorMessage = 'Data premiery nie może być późniejsza niż dzisiejsza';
                    }
                }
            } else if (fieldName === 'duration_minutes') {
                const value = parseInt(fields[fieldName].value);
                if (value && (value < 1 || value > 600)) {
                    isValid = false;
                    errorMessage = 'Czas trwania musi być między 1 a 600 minut';
                }
            }

            if (!isValid) {
                setFieldErrors(prev => ({ ...prev, [fieldName]: errorMessage }));
                toast.current?.show({
                    severity: 'error',
                    summary: 'Błąd walidacji',
                    detail: errorMessage,
                    life: 5000
                });
                return;
            }

            setSaveLoading(prev => ({ ...prev, [fieldName]: true }));
            setFieldErrors(prev => ({ ...prev, [fieldName]: '' }));

            const value = fields[fieldName].value;

            // Przygotuj dane do wysłania
            const formData = new FormData();
            formData.append(fieldName, value);

            await updateMovie(movieId, formData);

            // Zakończ tryb edycji
            toggleEdit(fieldName);

            // Odśwież dane filmu
            onRefresh();

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Pole zostało zaktualizowane',
                life: 3000
            });
        } catch (err: any) {
            setFieldErrors(prev => ({ ...prev, [fieldName]: err.message }));
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się zaktualizować pola',
                life: 5000
            });
            console.error(`Error updating ${fieldName}:`, err);
        } finally {
            setSaveLoading(prev => ({ ...prev, [fieldName]: false }));
        }
    };

    const handlePosterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setPosterFile(file);

            // Tworzenie podglądu plakatu
            const reader = new FileReader();
            reader.onloadend = () => {
                setPosterPreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handlePosterUpload = async () => {
        if (!posterFile) return;

        try {
            setSaveLoading(prev => ({ ...prev, 'poster': true }));

            await uploadMoviePoster(movieId, posterFile);

            // Odśwież dane filmu
            onRefresh();

            // Wyczyść stan
            setPosterFile(null);
            setPosterPreview(null);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Plakat został zaktualizowany',
                life: 3000
            });
        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się zaktualizować plakatu',
                life: 5000
            });
            console.error('Error uploading poster:', err);
        } finally {
            setSaveLoading(prev => ({ ...prev, 'poster': false }));
        }
    };

    const triggerPosterUpload = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    const cancelPosterUpload = () => {
        setPosterFile(null);
        setPosterPreview(null);
    };

    const formatDate = (dateString?: string): string => {
        if (!dateString) return '';
        return dateString.split('T')[0]; // Format YYYY-MM-DD
    };

    const confirmDelete = () => {
        confirmDialog({
            message: `Czy na pewno chcesz usunąć film "${movieData.title}"?`,
            header: 'Potwierdzenie usunięcia',
            icon: 'pi pi-exclamation-triangle',
            acceptClassName: 'p-button-danger',
            accept: handleDelete,
            reject: () => { }
        });
    };

    const handleDelete = async () => {
        try {
            setSaveLoading(prev => ({ ...prev, delete: true }));
            await deleteMovie(movieId);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Film został pomyślnie usunięty',
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
                detail: err.message || 'Nie udało się usunąć filmu',
                life: 5000
            });
            console.error('Error deleting movie:', err);
        } finally {
            setSaveLoading(prev => ({ ...prev, delete: false }));
        }
    };

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
            onRefresh();
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
            onRefresh();
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
            onRefresh();
        }
    };

    const handleAddActors = async (actors: { actorId: number; role: string }[]): Promise<boolean> => {
        try {
            let allSuccess = true;
            // Dodaj wszystkich aktorów jeden po drugim
            for (const actorData of actors) {
                const success = await addActor(actorData.actorId, actorData.role);
                if (!success) {
                    allSuccess = false;
                    break;
                }
            }
            if (allSuccess) {
                onRefresh();
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
            // Dodaj wszystkich reżyserów jeden po drugim
            for (const directorId of directorIds) {
                const success = await addDirector(directorId);
                if (!success) {
                    allSuccess = false;
                    break;
                }
            }
            if (allSuccess) {
                onRefresh();
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
            // Dodaj wszystkie gatunki jeden po drugim
            for (const genreId of genreIds) {
                const success = await addGenre(genreId);
                if (!success) {
                    allSuccess = false;
                    break;
                }
            }
            if (allSuccess) {
                onRefresh();
            }
            return allSuccess;
        } catch (error) {
            console.error('Error adding genres:', error);
            return false;
        }
    };

    const renderEditableField = (fieldName: string, label: string, type: 'text' | 'textarea' | 'date' | 'number' = 'text') => {
        const field = fields[fieldName];

        if (!field) return null;

        return (
            <div className={styles.detailItem}>
                <h3>{label}:</h3>
                {field.isEditing ? (
                    <div className={styles.editableFieldWrapper}>
                        {type === 'textarea' ? (
                            <textarea
                                ref={(el) => setInputRef(fieldName, el)}
                                value={field.value || ''}
                                onChange={(e) => updateField(fieldName, e.target.value)}
                                className={styles.editableInput}
                                rows={4}
                            />
                        ) : type === 'date' ? (
                            <input
                                type="date"
                                ref={(el) => setInputRef(fieldName, el)}
                                value={formatDate(field.value)}
                                onChange={(e) => updateField(fieldName, e.target.value)}
                                className={styles.editableInput}
                                max={formatDate(new Date().toISOString())}
                            />
                        ) : (
                            <>
                                <input
                                    type={type}
                                    ref={(el) => setInputRef(fieldName, el)}
                                    value={field.value || ''}
                                    onChange={(e) => updateField(fieldName, e.target.value)}
                                    className={styles.editableInput}
                                    maxLength={fieldName === 'title' ? 200 : undefined}
                                    min={type === 'number' ? 1 : undefined}
                                    max={type === 'number' ? 600 : undefined}
                                />
                                {fieldName === 'title' && (
                                    <div className={styles.fieldHint}>
                                        {field.value ? field.value.length : 0}/200 znaków
                                    </div>
                                )}
                                {fieldName === 'duration_minutes' && (
                                    <div className={styles.fieldHint}>
                                        Czas trwania w minutach (1-600)
                                    </div>
                                )}
                            </>
                        )}
                        <div className={styles.editActions}>
                            <button
                                onClick={() => handleFieldSave(fieldName)}
                                className={styles.saveButton}
                                disabled={saveLoading[fieldName]}
                            >
                                {saveLoading[fieldName] ? 'Zapisywanie...' : 'Zapisz'}
                            </button>
                            <button
                                onClick={() => toggleEdit(fieldName)}
                                className={styles.cancelButton}
                            >
                                Anuluj
                            </button>
                        </div>
                        {fieldErrors[fieldName] && (
                            <div className={styles.fieldError}>{fieldErrors[fieldName]}</div>
                        )}
                    </div>
                ) : (
                    <p
                        className={styles.editableText}
                        onClick={() => toggleEdit(fieldName)}
                    >
                        {field.value ? (type === 'date' ? formatDate(field.value) : field.value) :
                            <span className={styles.emptyValue}>Brak danych</span>}
                        <span className={styles.editIcon}>✎</span>
                    </p>
                )}
            </div>
        );
    };

    return (
        <div className={styles.container}>
            <Toast ref={toast} />
            <ConfirmDialog />

            <div className={styles.header}>
                <button
                    className={styles.backButton}
                    onClick={() => navigate('/dashboardpanel/movies/manage')}
                >
                    &larr; Powrót do listy
                </button>

                <h1 className={styles.title}>
                    Edycja filmu: {movieData.title}
                </h1>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}
            {relationsError && <div className={styles.errorMessage}>{relationsError}</div>}

            <div className={styles.movieDetailsCard}>
                <div className={styles.movieHeader}>
                    <div className={styles.posterContainer}>
                        {posterPreview ? (
                            <img src={posterPreview} alt={movieData.title} className={styles.moviePoster} />
                        ) : movieData.poster_url ? (
                            <img src={movieData.poster_url} alt={movieData.title} className={styles.moviePoster} />
                        ) : (
                            <div className={styles.moviePosterPlaceholder}>
                                {movieData.title.charAt(0).toUpperCase()}
                            </div>
                        )}

                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handlePosterChange}
                            accept="image/*"
                            style={{ display: 'none' }}
                        />

                        <button
                            className={styles.changePosterButton}
                            onClick={triggerPosterUpload}
                        >
                            Zmień plakat
                        </button>

                        {posterFile && (
                            <div className={styles.posterActions}>
                                <button
                                    onClick={handlePosterUpload}
                                    className={styles.saveButton}
                                    disabled={saveLoading['poster']}
                                >
                                    {saveLoading['poster'] ? 'Zapisywanie...' : 'Zapisz plakat'}
                                </button>
                                <button
                                    onClick={cancelPosterUpload}
                                    className={styles.cancelButton}
                                >
                                    Anuluj
                                </button>
                            </div>
                        )}
                    </div>

                    <div className={styles.movieInfo}>
                        <h2>{movieData.title}</h2>
                        <p className={styles.movieReleaseDate}>
                            {movieData.release_date ? formatDate(movieData.release_date) : 'Brak daty premiery'}
                        </p>
                        <p className={styles.movieDuration}>
                            {movieData.duration_minutes ? `${movieData.duration_minutes} min` : 'Brak czasu trwania'}
                        </p>
                    </div>
                </div>

                <div className={styles.movieDetailsContent}>
                    <div className={styles.movieDetailsGrid}>
                        {renderEditableField('title', 'Tytuł')}
                        {renderEditableField('release_date', 'Data premiery', 'date')}
                        {renderEditableField('duration_minutes', 'Czas trwania (min)', 'number')}
                        {renderEditableField('country', 'Kraj')}
                        {renderEditableField('original_language', 'Język oryginalny')}
                        {renderEditableField('trailer_url', 'URL zwiastuna')}

                        <div className={`${styles.detailItem} ${styles.descriptionField}`}>
                            {renderEditableField('description', 'Opis', 'textarea')}
                        </div>
                    </div>

                    {/* WYCIĄGNIĘTE KOMPONENTY */}
                    <ActorsSection
                        actors={movieData.actors}
                        onRemoveActor={handleRemoveActor}
                        onAddActors={handleAddActors}
                        relationsLoading={relationsLoading}
                    />

                    <DirectorsSection
                        directors={movieData.directors}
                        onRemoveDirector={handleRemoveDirector}
                        onAddDirectors={handleAddDirectors}
                        relationsLoading={relationsLoading}
                    />

                    <GenresSection
                        genres={movieData.genres}
                        onRemoveGenre={handleRemoveGenre}
                        onAddGenres={handleAddGenres}  // ZMIANA: onAddGenres zamiast onAddGenre
                        relationsLoading={relationsLoading}
                    />

                    <div className={styles.actionsFooter}>
                        <button
                            className={styles.deleteButton}
                            onClick={confirmDelete}
                            disabled={saveLoading.delete}
                        >
                            {saveLoading.delete ? 'Usuwanie...' : 'Usuń film'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MoviesEditPage;

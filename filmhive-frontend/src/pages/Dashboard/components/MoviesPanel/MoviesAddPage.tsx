import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { createMovie, uploadMoviePoster } from '../../services/movieService';
import styles from './MoviesAddPage.module.css';
import { Toast } from 'primereact/toast';

interface MovieFormData {
    title: string;
    release_date: string;
    duration_minutes: string;
    country: string;
    original_language: string;
    trailer_url: string;
    description: string;
    poster_url: string;
}

const MoviesAddPage: React.FC = () => {
    const navigate = useNavigate();
    const { isStaff } = useAuth();
    const [loading, setLoading] = useState<boolean>(false);
    const [formData, setFormData] = useState<MovieFormData>({
        title: '',
        release_date: '',
        duration_minutes: '',
        country: '',
        original_language: '',
        trailer_url: '',
        description: '',
        poster_url: ''
    });
    const [formErrors, setFormErrors] = useState<Record<string, string>>({});
    const [posterFile, setPosterFile] = useState<File | null>(null);
    const [posterPreview, setPosterPreview] = useState<string | null>(null);
    const [posterMode, setPosterMode] = useState<'file' | 'url'>('file');
    const fileInputRef = useRef<HTMLInputElement>(null);
    const toast = useRef<Toast>(null);

    const handleInputChange = (field: string, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        if (formErrors[field]) {
            setFormErrors(prev => ({ ...prev, [field]: '' }));
        }

        if (field === 'poster_url' && value && posterMode === 'url') {
            setPosterPreview(value);
        }
    };

    const handlePosterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setPosterFile(file);

            const reader = new FileReader();
            reader.onloadend = () => {
                setPosterPreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const triggerPosterUpload = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    const switchPosterMode = (mode: 'file' | 'url') => {
        setPosterMode(mode);
        setPosterFile(null);
        setPosterPreview(null);
        setFormData(prev => ({ ...prev, poster_url: '' }));
        if (formErrors.poster_url) {
            setFormErrors(prev => ({ ...prev, poster_url: '' }));
        }
    };

    const validateForm = (): boolean => {
        const errors: Record<string, string> = {};

        if (!formData.title.trim()) {
            errors.title = 'Tytuł jest wymagany';
        } else if (formData.title.length > 200) {
            errors.title = 'Tytuł nie może być dłuższy niż 200 znaków';
        }

        if (formData.trailer_url && formData.trailer_url.trim()) {
            try {
                new URL(formData.trailer_url.trim());
            } catch (e) {
                errors.trailer_url = 'Nieprawidłowy format URL';
            }
        }

        if (posterMode === 'url' && formData.poster_url && formData.poster_url.trim()) {
            try {
                new URL(formData.poster_url.trim());
            } catch (e) {
                errors.poster_url = 'Nieprawidłowy format URL plakatu';
            }
        }

        if (formData.release_date) {
            const selectedDate = new Date(formData.release_date);
            if (isNaN(selectedDate.getTime())) {
                errors.release_date = 'Nieprawidłowy format daty';
            }
        }

        if (formData.duration_minutes) {
            const duration = parseInt(formData.duration_minutes);
            if (isNaN(duration) || duration < 1 || duration > 600) {
                errors.duration_minutes = 'Czas trwania musi być między 1 a 600 minut';
            }
        }

        setFormErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleNext = async () => {
        if (!validateForm()) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd walidacji',
                detail: 'Popraw błędy w formularzu',
                life: 5000
            });
            return;
        }

        try {
            setLoading(true);

            const movieFormData = new FormData();
            movieFormData.append('title', formData.title);
            if (formData.release_date) movieFormData.append('release_date', formData.release_date);
            if (formData.duration_minutes) movieFormData.append('duration_minutes', formData.duration_minutes);
            if (formData.country) movieFormData.append('country', formData.country);
            if (formData.original_language) movieFormData.append('original_language', formData.original_language);
            if (formData.trailer_url) movieFormData.append('trailer_url', formData.trailer_url.trim());
            if (formData.description) movieFormData.append('description', formData.description);

            if (posterMode === 'file' && posterFile) {
                movieFormData.append('poster', posterFile);
            } else if (posterMode === 'url' && formData.poster_url) {
                movieFormData.append('poster_url', formData.poster_url.trim());
            }

            const newMovie = await createMovie(movieFormData);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Film został utworzony. Teraz możesz dodać aktorów, reżyserów i gatunki.',
                life: 3000
            });

            navigate(`/dashboardpanel/movies/add/${newMovie.id}/relations`);

        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się utworzyć filmu',
                life: 5000
            });
            console.error('Error creating movie:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        navigate('/dashboardpanel/movies/manage');
    };

    const renderFormField = (
        fieldName: keyof MovieFormData,
        label: string,
        type: 'text' | 'textarea' | 'date' | 'number' = 'text',
        required: boolean = false
    ) => {
        return (
            <div className={styles.formField}>
                <label className={styles.fieldLabel}>
                    {label}{required && <span className={styles.required}>*</span>}:
                </label>
                {type === 'textarea' ? (
                    <textarea
                        value={formData[fieldName]}
                        onChange={(e) => handleInputChange(fieldName, e.target.value)}
                        className={`${styles.formInput} ${formErrors[fieldName] ? styles.inputError : ''}`}
                        rows={4}
                        maxLength={1000}
                    />
                ) : type === 'date' ? (
                    <input
                        type="date"
                        value={formData[fieldName]}
                        onChange={(e) => handleInputChange(fieldName, e.target.value)}
                        className={`${styles.formInput} ${formErrors[fieldName] ? styles.inputError : ''}`}
                    />
                ) : (
                    <input
                        type={type}
                        value={formData[fieldName]}
                        onChange={(e) => handleInputChange(fieldName, e.target.value)}
                        className={`${styles.formInput} ${formErrors[fieldName] ? styles.inputError : ''}`}
                        maxLength={fieldName === 'title' ? 200 : undefined}
                        min={type === 'number' ? 1 : undefined}
                        max={type === 'number' ? 600 : undefined}
                        placeholder={
                            fieldName === 'trailer_url' ? 'https://www.youtube.com/watch?v=...' :
                                fieldName === 'poster_url' ? 'https://example.com/poster.jpg' : undefined
                        }
                    />
                )}
                {fieldName === 'title' && (
                    <div className={styles.fieldHint}>
                        {formData[fieldName].length}/200 znaków
                    </div>
                )}
                {fieldName === 'duration_minutes' && (
                    <div className={styles.fieldHint}>
                        Czas trwania w minutach (1-600)
                    </div>
                )}
                {fieldName === 'trailer_url' && (
                    <div className={styles.fieldHint}>
                        Podaj pełny URL zwiastuna
                    </div>
                )}
                {fieldName === 'poster_url' && (
                    <div className={styles.fieldHint}>
                        Podaj pełny URL plakatu
                    </div>
                )}
                {formErrors[fieldName] && (
                    <div className={styles.fieldError}>{formErrors[fieldName]}</div>
                )}
            </div>
        );
    };

    return (
        <div className={styles.container}>
            <Toast ref={toast} />

            <div className={styles.header}>
                <button
                    className={styles.backButton}
                    onClick={handleCancel}
                >
                    ← Powrót do listy
                </button>

                <h1 className={styles.title}>
                    Dodaj nowy film - Krok 1/2
                </h1>
            </div>

            <div className={styles.formCard}>
                <div className={styles.formHeader}>
                    <h2>Podstawowe informacje o filmie</h2>
                    <p className={styles.formDescription}>
                        Wypełnij podstawowe dane filmu. W następnym kroku będziesz mógł dodać aktorów, reżyserów i gatunki.
                    </p>
                </div>

                <div className={styles.formContent}>
                    <div className={styles.posterSection}>
                        <h3>Plakat filmu</h3>

                        <div className={styles.posterModeSelector}>
                            <button
                                type="button"
                                className={`${styles.modeButton} ${posterMode === 'file' ? styles.active : ''}`}
                                onClick={() => switchPosterMode('file')}
                            >
                                📁 Plik lokalny
                            </button>
                            <button
                                type="button"
                                className={`${styles.modeButton} ${posterMode === 'url' ? styles.active : ''}`}
                                onClick={() => switchPosterMode('url')}
                            >
                                🔗 Link z chmury
                            </button>
                        </div>

                        {posterMode === 'file' ? (
                            <div className={styles.posterContainer}>
                                {posterPreview ? (
                                    <img src={posterPreview} alt="Podgląd plakatu" className={styles.posterPreview} />
                                ) : (
                                    <div className={styles.posterPlaceholder}>
                                        <i className="pi pi-image" style={{ fontSize: '3rem', color: '#ccc' }}></i>
                                        <p>Brak plakatu</p>
                                    </div>
                                )}

                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handlePosterChange}
                                    accept="image/*"
                                    style={{ display: 'none' }}
                                />

                                <div className={styles.posterActions}>
                                    <button
                                        type="button"
                                        className={styles.selectPosterButton}
                                        onClick={triggerPosterUpload}
                                    >
                                        {posterFile ? 'Zmień plakat' : 'Wybierz plakat'}
                                    </button>
                                    {posterFile && (
                                        <button
                                            type="button"
                                            className={styles.removePosterButton}
                                            onClick={() => {
                                                setPosterFile(null);
                                                setPosterPreview(null);
                                            }}
                                        >
                                            Usuń
                                        </button>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <div className={styles.posterContainer}>
                                {posterPreview ? (
                                    <img src={posterPreview} alt="Podgląd plakatu" className={styles.posterPreview} />
                                ) : (
                                    <div className={styles.posterPlaceholder}>
                                        <i className="pi pi-image" style={{ fontSize: '3rem', color: '#ccc' }}></i>
                                        <p>Brak plakatu</p>
                                    </div>
                                )}

                                {renderFormField('poster_url', 'URL plakatu')}
                            </div>
                        )}
                    </div>

                    <div className={styles.formFields}>
                        {renderFormField('title', 'Tytuł', 'text', true)}
                        {renderFormField('release_date', 'Data premiery', 'date')}
                        {renderFormField('duration_minutes', 'Czas trwania (min)', 'number')}
                        {renderFormField('country', 'Kraj')}
                        {renderFormField('original_language', 'Język oryginalny')}
                        {renderFormField('trailer_url', 'URL zwiastuna')}
                        {renderFormField('description', 'Opis', 'textarea')}
                    </div>
                </div>

                <div className={styles.formFooter}>
                    <button
                        type="button"
                        className={styles.cancelButton}
                        onClick={handleCancel}
                    >
                        Anuluj
                    </button>
                    <button
                        type="button"
                        className={styles.nextButton}
                        onClick={handleNext}
                        disabled={loading}
                    >
                        {loading ? 'Tworzenie filmu...' : 'Dalej - Dodaj relacje'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MoviesAddPage;

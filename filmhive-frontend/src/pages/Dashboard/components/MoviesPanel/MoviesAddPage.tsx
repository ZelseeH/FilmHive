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
        description: ''
    });
    const [formErrors, setFormErrors] = useState<Record<string, string>>({});
    const [posterFile, setPosterFile] = useState<File | null>(null);
    const [posterPreview, setPosterPreview] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const toast = useRef<Toast>(null);

    const handleInputChange = (field: string, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Wyczyść błąd dla tego pola
        if (formErrors[field]) {
            setFormErrors(prev => ({ ...prev, [field]: '' }));
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

    const validateForm = (): boolean => {
        const errors: Record<string, string> = {};

        // Walidacja tytułu
        if (!formData.title.trim()) {
            errors.title = 'Tytuł jest wymagany';
        } else if (formData.title.length > 200) {
            errors.title = 'Tytuł nie może być dłuższy niż 200 znaków';
        }

        // Walidacja daty premiery
        if (formData.release_date) {
            const selectedDate = new Date(formData.release_date);
            const today = new Date();
            if (selectedDate > today) {
                errors.release_date = 'Data premiery nie może być późniejsza niż dzisiejsza';
            }
        }

        // Walidacja czasu trwania
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

            // Przygotuj dane do wysłania
            const movieFormData = new FormData();
            movieFormData.append('title', formData.title);
            if (formData.release_date) movieFormData.append('release_date', formData.release_date);
            if (formData.duration_minutes) movieFormData.append('duration_minutes', formData.duration_minutes);
            if (formData.country) movieFormData.append('country', formData.country);
            if (formData.original_language) movieFormData.append('original_language', formData.original_language);
            if (formData.trailer_url) movieFormData.append('trailer_url', formData.trailer_url);
            if (formData.description) movieFormData.append('description', formData.description);

            // Dodaj plakat jeśli został wybrany
            if (posterFile) {
                movieFormData.append('poster', posterFile);
            }

            // Stwórz film w bazie danych
            const newMovie = await createMovie(movieFormData);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Film został utworzony. Teraz możesz dodać aktorów, reżyserów i gatunki.',
                life: 3000
            });

            // POPRAWIONE PRZEKIEROWANIE do etapu 2
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
                        max={formatDate(new Date().toISOString())}
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
                    &larr; Powrót do listy
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
                                        onClick={cancelPosterUpload}
                                    >
                                        Usuń
                                    </button>
                                )}
                            </div>
                        </div>
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

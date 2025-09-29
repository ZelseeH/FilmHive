import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { createDirector } from '../../services/directorService';
import ImageSelector from '../ImgSelector/ImageSelector';
import styles from './DirectorsAddPage.module.css';
import { Toast } from 'primereact/toast';
import { ConfirmDialog } from 'primereact/confirmdialog';

const DirectorsAddPage: React.FC = () => {
    const navigate = useNavigate();
    const { isStaff } = useAuth();
    const toast = useRef<Toast>(null);

    const [loading, setLoading] = useState<boolean>(false);
    const [formData, setFormData] = useState({
        name: '',
        birth_date: '',
        birth_place: '',
        biography: '',
        gender: '' as '' | 'M' | 'K'
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    // ImageSelector state
    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [photoUrl, setPhotoUrl] = useState<string | null>(null);
    const [photoPreview, setPhotoPreview] = useState<string | null>(null);

    // Sprawdzenie uprawnień
    if (!isStaff()) {
        return (
            <div className={styles.container}>
                <div className={styles.errorMessage}>
                    Nie masz uprawnień do dodawania reżyserów.
                </div>
            </div>
        );
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        validateField(name, value);
    };

    const validateField = (name: string, value: string) => {
        const newErrors = { ...errors };

        switch (name) {
            case 'name':
                if (!value) {
                    newErrors.name = 'Imię i nazwisko jest wymagane';
                } else if (value.length > 100) {
                    newErrors.name = 'Imię i nazwisko nie może być dłuższe niż 100 znaków';
                } else {
                    delete newErrors.name;
                }
                break;

            case 'birth_date':
                if (!value) {
                    newErrors.birth_date = 'Data urodzenia jest wymagana';
                } else {
                    delete newErrors.birth_date;
                }
                break;

            case 'birth_place':
                if (!value.trim()) {
                    newErrors.birth_place = 'Miejsce urodzenia jest wymagane';
                } else if (!value.includes(',')) {
                    newErrors.birth_place = 'Miejsce urodzenia musi być w formacie: Miasto, Kraj';
                } else {
                    const parts = value.split(',');
                    if (parts.length !== 2 || !parts[0].trim() || !parts[1].trim()) {
                        newErrors.birth_place = 'Miejsce urodzenia musi być w formacie: Miasto, Kraj';
                    } else {
                        delete newErrors.birth_place;
                    }
                }
                break;

            case 'gender':
                if (!value) {
                    newErrors.gender = 'Płeć jest wymagana';
                } else {
                    delete newErrors.gender;
                }
                break;

            default:
                break;
        }

        setErrors(newErrors);
    };

    // ImageSelector handlers
    const handleImageChange = (file: File | null, url: string | null) => {
        setPhotoFile(file);
        setPhotoUrl(url);

        // Wyczyść błąd zdjęcia gdy coś zostało wybrane
        if (file || url) {
            setErrors(prev => ({ ...prev, photo: '' }));
        }
    };

    const handlePreviewChange = (preview: string | null) => {
        setPhotoPreview(preview);
    };

    const validateForm = (): boolean => {
        // Walidacja wszystkich pól
        validateField('name', formData.name);
        validateField('birth_date', formData.birth_date);
        validateField('birth_place', formData.birth_place);
        validateField('gender', formData.gender);

        // Sprawdź, czy zdjęcie zostało wybrane
        const newErrors = { ...errors };
        if (!photoFile && !photoUrl) {
            newErrors.photo = 'Zdjęcie jest wymagane';
        } else {
            delete newErrors.photo;
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd walidacji',
                detail: 'Popraw błędy w formularzu',
                life: 3000
            });
            return;
        }

        try {
            setLoading(true);

            const directorFormData = new FormData();
            directorFormData.append('name', formData.name);
            directorFormData.append('birth_date', formData.birth_date);
            directorFormData.append('birth_place', formData.birth_place);

            if (formData.biography) {
                directorFormData.append('biography', formData.biography);
            }

            directorFormData.append('gender', formData.gender);

            // DEBUGOWANIE - sprawdź co wysyłasz
            console.log('🔍 PRZED WYSŁANIEM REŻYSERA:');
            console.log('Photo file:', photoFile);
            console.log('Photo URL:', photoUrl);

            // Dodaj zdjęcie - plik lokalny lub URL
            if (photoFile) {
                console.log('📁 Wysyłam plik reżysera:', photoFile.name, photoFile.size);
                directorFormData.append('photo', photoFile);
            } else if (photoUrl) {
                console.log('🔗 Wysyłam URL reżysera:', photoUrl);
                directorFormData.append('photo_url', photoUrl.trim());
            } else {
                console.log('❌ Brak zdjęcia reżysera!');
            }

            // DEBUG FormData - POPRAWIONA WERSJA
            console.log('📋 FormData reżysera zawiera:');
            const formDataEntries = Array.from(directorFormData.entries());
            formDataEntries.forEach(([key, value]) => {
                if (value instanceof File) {
                    console.log(`${key}: [File] ${value.name} (${value.size} bytes)`);
                } else {
                    console.log(`${key}: ${value}`);
                }
            });

            const result = await createDirector(directorFormData);
            console.log('✅ Odpowiedź serwera (reżyser):', result);

            // Sprawdź czy photo_url zostało zapisane
            if (result.photo_url) {
                console.log('🎉 Photo URL reżysera zapisane w bazie:', result.photo_url);
            } else {
                console.log('⚠️ Photo URL reżysera NIE zostało zapisane!');
            }

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Reżyser został pomyślnie dodany',
                life: 3000
            });

            setTimeout(() => {
                navigate('/dashboardpanel/directors/manage');
            }, 1500);

        } catch (err: any) {
            console.error('❌ BŁĄD TWORZENIA REŻYSERA:', err);
            const errorMessage = err.message || 'Wystąpił błąd podczas dodawania reżysera';
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: errorMessage,
                life: 5000
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <Toast ref={toast} />
            <ConfirmDialog />

            <div className={styles.header}>
                <button
                    className={styles.backButton}
                    onClick={() => navigate('/dashboardpanel/directors/manage')}
                >
                    ← Powrót do listy
                </button>

                <h1 className={styles.title}>
                    Dodaj nowego reżysera
                </h1>
            </div>

            <div className={styles.directorDetailsCard}>
                <form onSubmit={handleSubmit}>
                    <div className={styles.directorHeader}>
                        <div className={styles.photoContainer}>
                            <ImageSelector
                                onImageChange={handleImageChange}
                                onPreviewChange={handlePreviewChange}
                                label="Zdjęcie reżysera"
                                placeholder="Brak zdjęcia"
                                maxFileSize={5}
                                required={true}
                                error={errors.photo}
                                disabled={loading}
                                className={styles.directorImageSelector}
                            />
                        </div>

                        <div className={styles.directorInfo}>
                            <h2>Nowy reżyser</h2>
                            <p className={styles.directorInfoText}>
                                Uzupełnij dane nowego reżysera
                            </p>
                            <p className={styles.requiredFieldsInfo}>
                                * Pola wymagane
                            </p>
                        </div>
                    </div>

                    <div className={styles.directorDetailsContent}>
                        <div className={styles.directorDetailsGrid}>
                            <div className={styles.formGroup}>
                                <label htmlFor="name">Imię i nazwisko*</label>
                                <input
                                    type="text"
                                    id="name"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    className={`${styles.input} ${errors.name ? styles.inputError : ''}`}
                                    maxLength={100}
                                    disabled={loading}
                                    required
                                />
                                <div className={styles.fieldHint}>
                                    {formData.name.length}/100 znaków
                                </div>
                                {errors.name && <div className={styles.fieldError}>{errors.name}</div>}
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="birth_date">Data urodzenia*</label>
                                <input
                                    type="date"
                                    id="birth_date"
                                    name="birth_date"
                                    value={formData.birth_date}
                                    onChange={handleInputChange}
                                    className={`${styles.input} ${errors.birth_date ? styles.inputError : ''}`}
                                    disabled={loading}
                                    required
                                />
                                {errors.birth_date && <div className={styles.fieldError}>{errors.birth_date}</div>}
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="birth_place">Miejsce urodzenia* (Miasto, Kraj)</label>
                                <input
                                    type="text"
                                    id="birth_place"
                                    name="birth_place"
                                    value={formData.birth_place}
                                    onChange={handleInputChange}
                                    placeholder="np. Warszawa, Polska"
                                    className={`${styles.input} ${errors.birth_place ? styles.inputError : ''}`}
                                    disabled={loading}
                                    required
                                />
                                {errors.birth_place && <div className={styles.fieldError}>{errors.birth_place}</div>}
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="gender">Płeć*</label>
                                <select
                                    id="gender"
                                    name="gender"
                                    value={formData.gender}
                                    onChange={handleInputChange}
                                    className={`${styles.input} ${errors.gender ? styles.inputError : ''}`}
                                    disabled={loading}
                                    required
                                >
                                    <option value="">Wybierz płeć</option>
                                    <option value="M">Mężczyzna</option>
                                    <option value="K">Kobieta</option>
                                </select>
                                {errors.gender && <div className={styles.fieldError}>{errors.gender}</div>}
                            </div>

                            <div className={`${styles.formGroup} ${styles.bioField}`}>
                                <label htmlFor="biography">Biografia</label>
                                <textarea
                                    id="biography"
                                    name="biography"
                                    value={formData.biography}
                                    onChange={handleInputChange}
                                    className={styles.textarea}
                                    rows={4}
                                    placeholder="Opcjonalnie"
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        <div className={styles.actionsFooter}>
                            <button
                                type="submit"
                                className={styles.submitButton}
                                disabled={loading}
                            >
                                {loading ? 'Dodawanie...' : 'Dodaj reżysera'}
                            </button>
                            <button
                                type="button"
                                className={styles.cancelButton}
                                onClick={() => navigate('/dashboardpanel/directors/manage')}
                                disabled={loading}
                            >
                                Anuluj
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default DirectorsAddPage;

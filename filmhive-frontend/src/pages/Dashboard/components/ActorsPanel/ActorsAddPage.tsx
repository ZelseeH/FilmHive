import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { createActor } from '../../services/actorService';
import styles from './ActorsAddPage.module.css';
import { Toast } from 'primereact/toast';
import { ConfirmDialog } from 'primereact/confirmdialog';

const ActorsAddPage: React.FC = () => {
    const navigate = useNavigate();
    const { isStaff } = useAuth();
    const toast = useRef<Toast>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [loading, setLoading] = useState<boolean>(false);
    const [formData, setFormData] = useState({
        name: '',
        birth_date: '',
        birth_place: '',
        biography: '',
        gender: '' as '' | 'M' | 'K'
    });
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [photoPreview, setPhotoPreview] = useState<string | null>(null);

    // Sprawdzenie uprawnień
    if (!isStaff()) {
        return (
            <div className={styles.container}>
                <div className={styles.errorMessage}>
                    Nie masz uprawnień do dodawania aktorów.
                </div>
            </div>
        );
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));

        // Walidacja w trakcie wpisywania
        validateField(name, value);
    };

    const validateField = (name: string, value: string) => {
        const newErrors = { ...errors };

        switch (name) {
            case 'name':
                if (!value.trim()) {
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
                    const selectedDate = new Date(value);
                    const today = new Date();
                    if (selectedDate > today) {
                        newErrors.birth_date = 'Data urodzenia nie może być późniejsza niż dzisiejsza';
                    } else {
                        delete newErrors.birth_date;
                    }
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

    const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setPhotoFile(file);

            // Tworzenie podglądu zdjęcia
            const reader = new FileReader();
            reader.onloadend = () => {
                setPhotoPreview(reader.result as string);
            };
            reader.readAsDataURL(file);

            // Wyczyść błąd po wybraniu zdjęcia
            setErrors(prev => ({ ...prev, photo: '' }));
        }
    };

    const triggerPhotoUpload = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    const validateForm = (): boolean => {
        // Walidacja wszystkich pól
        validateField('name', formData.name);
        validateField('birth_date', formData.birth_date);
        validateField('birth_place', formData.birth_place);
        validateField('gender', formData.gender);

        // Sprawdź, czy zdjęcie zostało wybrane
        const newErrors = { ...errors };
        if (!photoFile) {
            newErrors.photo = 'Zdjęcie jest wymagane';
        } else {
            delete newErrors.photo;
        }

        setErrors(newErrors);

        // Sprawdź, czy są jakiekolwiek błędy
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

            const actorFormData = new FormData();
            actorFormData.append('name', formData.name);
            actorFormData.append('birth_date', formData.birth_date);
            actorFormData.append('birth_place', formData.birth_place);

            if (formData.biography) {
                actorFormData.append('biography', formData.biography);
            }

            actorFormData.append('gender', formData.gender);

            if (photoFile) {
                actorFormData.append('photo', photoFile);
            }

            const result = await createActor(actorFormData);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Aktor został pomyślnie dodany',
                life: 3000
            });

            // Przekieruj do listy aktorów po krótkim opóźnieniu
            setTimeout(() => {
                navigate('/dashboardpanel/actors/manage');
            }, 1500);

        } catch (err: any) {
            const errorMessage = err.message || 'Wystąpił błąd podczas dodawania aktora';
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: errorMessage,
                life: 5000
            });
            console.error('Error adding actor:', err);
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
                    onClick={() => navigate('/dashboardpanel/actors/manage')}
                >
                    &larr; Powrót do listy
                </button>

                <h1 className={styles.title}>
                    Dodaj nowego aktora
                </h1>
            </div>

            <div className={styles.actorDetailsCard}>
                <form onSubmit={handleSubmit}>
                    <div className={styles.actorHeader}>
                        <div className={styles.photoContainer}>
                            {photoPreview ? (
                                <img src={photoPreview} alt="Podgląd zdjęcia" className={styles.actorPhoto} />
                            ) : (
                                <div
                                    className={`${styles.actorPhotoPlaceholder} ${errors.photo ? styles.photoError : ''}`}
                                    onClick={triggerPhotoUpload}
                                >
                                    +
                                </div>
                            )}

                            <input
                                type="file"
                                ref={fileInputRef}
                                onChange={handlePhotoChange}
                                accept="image/*"
                                style={{ display: 'none' }}
                            />

                            <button
                                type="button"
                                className={styles.changePhotoButton}
                                onClick={triggerPhotoUpload}
                            >
                                {photoPreview ? 'Zmień zdjęcie' : 'Dodaj zdjęcie*'}
                            </button>

                            {errors.photo && <div className={styles.fieldError}>{errors.photo}</div>}
                        </div>

                        <div className={styles.actorInfo}>
                            <h2>Nowy aktor</h2>
                            <p className={styles.actorInfoText}>
                                Uzupełnij dane nowego aktora
                            </p>
                            <p className={styles.requiredFieldsInfo}>
                                * Pola wymagane
                            </p>
                        </div>
                    </div>

                    <div className={styles.actorDetailsContent}>
                        <div className={styles.actorDetailsGrid}>
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
                                    max={new Date().toISOString().split('T')[0]}
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
                                />
                            </div>
                        </div>

                        <div className={styles.actionsFooter}>
                            <button
                                type="submit"
                                className={styles.submitButton}
                                disabled={loading}
                            >
                                {loading ? 'Dodawanie...' : 'Dodaj aktora'}
                            </button>
                            <button
                                type="button"
                                className={styles.cancelButton}
                                onClick={() => navigate('/dashboardpanel/actors/manage')}
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

export default ActorsAddPage;

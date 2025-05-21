import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { getActorById, updateActor, uploadActorPhoto, deleteActor } from '../../services/actorService';
import { useInlineEdit } from '../../hooks/useInlineEdit';
import styles from './ActorsEditPage.module.css';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Toast } from 'primereact/toast';

interface ActorEditParams {
    id: string;
}

const ActorsEditPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { getToken, isStaff } = useAuth();
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [actorData, setActorData] = useState<any>(null);

    // Pobieranie ID aktora z parametru URL
    const actorId = id ? parseInt(id) : undefined;

    useEffect(() => {
        if (actorId) {
            fetchActorDetails(actorId);
        }
    }, [actorId]);

    const fetchActorDetails = async (actorId: number) => {
        try {
            setLoading(true);
            const data = await getActorById(actorId);
            setActorData(data);
            setError(null);
        } catch (err: any) {
            setError(err.message);
            console.error('Error fetching actor details:', err);
        } finally {
            setLoading(false);
        }
    };

    // Jeśli dane aktora nie są jeszcze załadowane, nie inicjalizuj hooka
    if (!actorData && !loading) {
        return <div className={styles.errorMessage}>Nie można załadować danych aktora</div>;
    }

    if (loading) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p>Ładowanie danych aktora...</p>
            </div>
        );
    }

    return (
        <ActorEditContent
            actorData={actorData}
            actorId={actorId as number}
            error={error}
            onRefresh={() => fetchActorDetails(actorId as number)}
            navigate={navigate}
        />
    );
};

interface ActorEditContentProps {
    actorData: any;
    actorId: number;
    error: string | null;
    onRefresh: () => void;
    navigate: any;
}

const ActorEditContent: React.FC<ActorEditContentProps> = ({
    actorData,
    actorId,
    error,
    onRefresh,
    navigate
}) => {
    const { fields, toggleEdit, updateField, cancelEdit, getValues, setInputRef } = useInlineEdit(actorData);
    const [saveLoading, setSaveLoading] = useState<Record<string, boolean>>({});
    const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [photoPreview, setPhotoPreview] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const toast = useRef<Toast>(null);

    const handleFieldSave = async (fieldName: string) => {
        try {
            // Walidacja pól przed zapisem
            let isValid = true;
            let errorMessage = '';

            if (fieldName === 'name') {
                const value = fields[fieldName].value;
                if (!value || !value.trim()) {
                    isValid = false;
                    errorMessage = 'Imię i nazwisko jest wymagane';
                } else if (value.length > 100) {
                    isValid = false;
                    errorMessage = 'Imię i nazwisko nie może być dłuższe niż 100 znaków';
                }
            } else if (fieldName === 'birth_date') {
                const value = fields[fieldName].value;
                if (value) {
                    const selectedDate = new Date(value);
                    const today = new Date();
                    if (selectedDate > today) {
                        isValid = false;
                        errorMessage = 'Data urodzenia nie może być późniejsza niż dzisiejsza';
                    }
                }
            } else if (fieldName === 'birth_place') {
                const value = fields[fieldName].value;
                if (!value || !value.trim()) {
                    isValid = false;
                    errorMessage = 'Miejsce urodzenia jest wymagane';
                } else if (!value.includes(',')) {
                    isValid = false;
                    errorMessage = 'Miejsce urodzenia musi być w formacie: Miasto, Kraj';
                } else {
                    const parts = value.split(',');
                    if (parts.length !== 2 || !parts[0].trim() || !parts[1].trim()) {
                        isValid = false;
                        errorMessage = 'Miejsce urodzenia musi być w formacie: Miasto, Kraj';
                    }
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

            await updateActor(actorId, formData);

            // Zakończ tryb edycji
            toggleEdit(fieldName);

            // Odśwież dane aktora
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

    const handleGenderChange = async (newGender: 'M' | 'K' | null) => {
        try {
            setSaveLoading(prev => ({ ...prev, 'gender': true }));

            const formData = new FormData();
            formData.append('gender', newGender || '');

            await updateActor(actorId, formData);
            onRefresh();

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Płeć została zaktualizowana',
                life: 3000
            });
        } catch (err: any) {
            setFieldErrors(prev => ({ ...prev, 'gender': err.message }));
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się zaktualizować płci',
                life: 5000
            });
            console.error('Error updating gender:', err);
        } finally {
            setSaveLoading(prev => ({ ...prev, 'gender': false }));
        }
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
        }
    };

    const handlePhotoUpload = async () => {
        if (!photoFile) return;

        try {
            setSaveLoading(prev => ({ ...prev, 'photo': true }));

            await uploadActorPhoto(actorId, photoFile);

            // Odśwież dane aktora
            onRefresh();

            // Wyczyść stan
            setPhotoFile(null);
            setPhotoPreview(null);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Zdjęcie zostało zaktualizowane',
                life: 3000
            });
        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się zaktualizować zdjęcia',
                life: 5000
            });
            console.error('Error uploading photo:', err);
        } finally {
            setSaveLoading(prev => ({ ...prev, 'photo': false }));
        }
    };

    const triggerPhotoUpload = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    const cancelPhotoUpload = () => {
        setPhotoFile(null);
        setPhotoPreview(null);
    };

    const formatDate = (dateString?: string): string => {
        if (!dateString) return '';
        return dateString.split('T')[0]; // Format YYYY-MM-DD
    };

    const confirmDelete = () => {
        confirmDialog({
            message: `Czy na pewno chcesz usunąć aktora ${actorData.name}?`,
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
            await deleteActor(actorId);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Aktor został pomyślnie usunięty',
                life: 3000
            });

            // Przekieruj do listy aktorów po krótkim opóźnieniu
            setTimeout(() => {
                navigate('/dashboardpanel/actors/manage');
            }, 1500);
        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się usunąć aktora',
                life: 5000
            });
            console.error('Error deleting actor:', err);
        } finally {
            setSaveLoading(prev => ({ ...prev, delete: false }));
        }
    };

    const renderEditableField = (fieldName: string, label: string, type: 'text' | 'textarea' | 'date' = 'text') => {
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
                                    maxLength={fieldName === 'name' ? 100 : undefined}
                                />
                                {fieldName === 'name' && (
                                    <div className={styles.fieldHint}>
                                        {field.value ? field.value.length : 0}/100 znaków
                                    </div>
                                )}
                                {fieldName === 'birth_place' && (
                                    <div className={styles.fieldHint}>
                                        Format: Miasto, Kraj
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

    const getGenderName = (gender: string | null): string => {
        switch (gender) {
            case 'M': return 'Mężczyzna';
            case 'K': return 'Kobieta';
            default: return 'Nie określono';
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
                    Edycja aktora: {actorData.name}
                </h1>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div className={styles.actorDetailsCard}>
                <div className={styles.actorHeader}>
                    <div className={styles.photoContainer}>
                        {photoPreview ? (
                            <img src={photoPreview} alt={actorData.name} className={styles.actorPhoto} />
                        ) : actorData.photo_url ? (
                            <img src={actorData.photo_url} alt={actorData.name} className={styles.actorPhoto} />
                        ) : (
                            <div className={styles.actorPhotoPlaceholder}>
                                {actorData.name.charAt(0).toUpperCase()}
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
                            className={styles.changePhotoButton}
                            onClick={triggerPhotoUpload}
                        >
                            Zmień zdjęcie
                        </button>

                        {photoFile && (
                            <div className={styles.photoActions}>
                                <button
                                    onClick={handlePhotoUpload}
                                    className={styles.saveButton}
                                    disabled={saveLoading['photo']}
                                >
                                    {saveLoading['photo'] ? 'Zapisywanie...' : 'Zapisz zdjęcie'}
                                </button>
                                <button
                                    onClick={cancelPhotoUpload}
                                    className={styles.cancelButton}
                                >
                                    Anuluj
                                </button>
                            </div>
                        )}
                    </div>

                    <div className={styles.actorInfo}>
                        <h2>{actorData.name}</h2>
                        <p className={styles.actorBirthDate}>
                            {actorData.birth_date ? formatDate(actorData.birth_date) : 'Brak daty urodzenia'}
                        </p>
                        <p className={styles.actorGender}>{getGenderName(actorData.gender)}</p>
                    </div>
                </div>

                <div className={styles.actorDetailsContent}>
                    <div className={styles.actorDetailsGrid}>
                        {renderEditableField('name', 'Imię i nazwisko')}
                        {renderEditableField('birth_date', 'Data urodzenia', 'date')}
                        {renderEditableField('birth_place', 'Miejsce urodzenia')}

                        <div className={styles.detailItem}>
                            <h3>Płeć:</h3>
                            <div className={styles.genderToggle}>
                                <button
                                    onClick={() => handleGenderChange('M')}
                                    className={`${styles.genderButton} ${actorData.gender === 'M' ? styles.genderButtonActive : ''}`}
                                    disabled={actorData.gender === 'M' || saveLoading['gender']}
                                >
                                    Mężczyzna
                                </button>
                                <button
                                    onClick={() => handleGenderChange('K')}
                                    className={`${styles.genderButton} ${actorData.gender === 'K' ? styles.genderButtonActive : ''}`}
                                    disabled={actorData.gender === 'K' || saveLoading['gender']}
                                >
                                    Kobieta
                                </button>
                                <button
                                    onClick={() => handleGenderChange(null)}
                                    className={`${styles.genderButton} ${actorData.gender === null ? styles.genderButtonActive : ''}`}
                                    disabled={actorData.gender === null || saveLoading['gender']}
                                >
                                    Nie określono
                                </button>
                                {saveLoading['gender'] && <span className={styles.miniSpinner}></span>}
                            </div>
                            {fieldErrors['gender'] && (
                                <div className={styles.fieldError}>{fieldErrors['gender']}</div>
                            )}
                        </div>

                        <div className={`${styles.detailItem} ${styles.bioField}`}>
                            {renderEditableField('biography', 'Biografia', 'textarea')}
                        </div>
                    </div>

                    <div className={styles.actionsFooter}>
                        <button
                            className={styles.deleteButton}
                            onClick={confirmDelete}
                            disabled={saveLoading.delete}
                        >
                            {saveLoading.delete ? 'Usuwanie...' : 'Usuń aktora'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ActorsEditPage;

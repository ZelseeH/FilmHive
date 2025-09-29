import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { getDirectorById, updateDirector, uploadDirectorPhoto, deleteDirector } from '../../services/directorService';
import { useInlineEdit } from '../../hooks/useInlineEdit';
import ImageSelector from '../ImgSelector/ImageSelector';
import styles from './DirectorsEditPage.module.css';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Toast } from 'primereact/toast';

const DirectorsEditPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { getToken, isStaff } = useAuth();
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [directorData, setDirectorData] = useState<any>(null);

    // Pobieranie ID reżysera z parametru URL
    const directorId = id ? parseInt(id) : undefined;

    useEffect(() => {
        if (directorId) {
            fetchDirectorDetails(directorId);
        }
    }, [directorId]);

    const fetchDirectorDetails = async (directorId: number) => {
        try {
            setLoading(true);
            const data = await getDirectorById(directorId);
            setDirectorData(data);
            setError(null);
        } catch (err: any) {
            setError(err.message);
            console.error('Error fetching director details:', err);
        } finally {
            setLoading(false);
        }
    };

    // Jeśli dane reżysera nie są jeszcze załadowane, nie inicjalizuj hooka
    if (!directorData && !loading) {
        return <div className={styles.errorMessage}>Nie można załadować danych reżysera</div>;
    }

    if (loading) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p>Ładowanie danych reżysera...</p>
            </div>
        );
    }

    return (
        <DirectorEditContent
            directorData={directorData}
            directorId={directorId as number}
            error={error}
            onRefresh={() => fetchDirectorDetails(directorId as number)}
            navigate={navigate}
        />
    );
};

interface DirectorEditContentProps {
    directorData: any;
    directorId: number;
    error: string | null;
    onRefresh: () => void;
    navigate: any;
}

const DirectorEditContent: React.FC<DirectorEditContentProps> = ({
    directorData,
    directorId,
    error,
    onRefresh,
    navigate
}) => {
    const { fields, toggleEdit, updateField, cancelEdit, getValues, setInputRef } = useInlineEdit(directorData);
    const [saveLoading, setSaveLoading] = useState<Record<string, boolean>>({});
    const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

    // ImageSelector state
    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [photoUrl, setPhotoUrl] = useState<string | null>(null);
    const [photoPreview, setPhotoPreview] = useState<string | null>(null);
    const [isEditingPhoto, setIsEditingPhoto] = useState<boolean>(false);
    const [photoError, setPhotoError] = useState<string>('');

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

            await updateDirector(directorId, formData);

            // Zakończ tryb edycji
            toggleEdit(fieldName);

            // Odśwież dane reżysera
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

            await updateDirector(directorId, formData);
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

    // ImageSelector handlers
    const handleImageChange = (file: File | null, url: string | null) => {
        setPhotoFile(file);
        setPhotoUrl(url);
        setPhotoError('');
    };

    const handlePreviewChange = (preview: string | null) => {
        setPhotoPreview(preview);
    };

    const handlePhotoSave = async () => {
        if (!photoFile && !photoUrl) {
            setPhotoError('Wybierz zdjęcie');
            return;
        }

        try {
            setSaveLoading(prev => ({ ...prev, 'photo': true }));
            setPhotoError('');

            const formData = new FormData();

            if (photoFile) {
                // Plik lokalny
                formData.append('photo', photoFile);
            } else if (photoUrl) {
                // URL z internetu
                formData.append('photo_url', photoUrl);
            }

            // DEBUG FormData - POPRAWIONA WERSJA
            console.log('📋 FormData reżysera zawiera:');
            const formDataEntries = Array.from(formData.entries());
            formDataEntries.forEach(([key, value]) => {
                if (value instanceof File) {
                    console.log(`${key}: [File] ${value.name} (${value.size} bytes)`);
                } else {
                    console.log(`${key}: ${value}`);
                }
            });

            await updateDirector(directorId, formData);

            // Odśwież dane reżysera
            onRefresh();

            // Wyczyść stan i zakończ edycję
            setPhotoFile(null);
            setPhotoUrl(null);
            setPhotoPreview(null);
            setIsEditingPhoto(false);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Zdjęcie zostało zaktualizowane',
                life: 3000
            });
        } catch (err: any) {
            setPhotoError(err.message || 'Nie udało się zaktualizować zdjęcia');
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się zaktualizować zdjęcia',
                life: 5000
            });
            console.error('Error updating photo:', err);
        } finally {
            setSaveLoading(prev => ({ ...prev, 'photo': false }));
        }
    };

    const handlePhotoCancelEdit = () => {
        setPhotoFile(null);
        setPhotoUrl(null);
        setPhotoPreview(null);
        setIsEditingPhoto(false);
        setPhotoError('');
    };

    const formatDate = (dateString?: string): string => {
        if (!dateString) return '';
        return dateString.split('T')[0]; // Format YYYY-MM-DD
    };

    const confirmDelete = () => {
        confirmDialog({
            message: `Czy na pewno chcesz usunąć reżysera ${directorData.name}?`,
            header: 'Potwierdzenie usunięcia',
            icon: 'pi pi-exclamation-triangle',
            acceptClassName: 'p-button-danger',
            acceptLabel: 'Tak',
            rejectLabel: 'Nie',
            accept: handleDelete,
            reject: () => { }
        });
    };


    const handleDelete = async () => {
        try {
            setSaveLoading(prev => ({ ...prev, delete: true }));
            await deleteDirector(directorId);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Reżyser został pomyślnie usunięty',
                life: 3000
            });

            // Przekieruj do listy reżyserów po krótkim opóźnieniu
            setTimeout(() => {
                navigate('/dashboardpanel/directors/manage');
            }, 1500);
        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się usunąć reżysera',
                life: 5000
            });
            console.error('Error deleting director:', err);
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
                    onClick={() => navigate('/dashboardpanel/directors/manage')}
                >
                    &larr; Powrót do listy
                </button>

                <h1 className={styles.title}>
                    Edycja reżysera: {directorData.name}
                </h1>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div className={styles.directorDetailsCard}>
                <div className={styles.directorHeader}>
                    <div className={styles.photoContainer}>
                        {isEditingPhoto ? (
                            <div className={styles.photoEditContainer}>
                                <ImageSelector
                                    currentImage={directorData.photo_url}
                                    onImageChange={handleImageChange}
                                    onPreviewChange={handlePreviewChange}
                                    label="Zdjęcie reżysera"
                                    placeholder="Brak zdjęcia"
                                    maxFileSize={5}
                                    required={false}
                                    error={photoError}
                                    disabled={saveLoading['photo']}
                                    className={styles.directorImageSelector}
                                />

                                <div className={styles.photoEditActions}>
                                    <button
                                        onClick={handlePhotoSave}
                                        className={styles.saveButton}
                                        disabled={saveLoading['photo']}
                                    >
                                        {saveLoading['photo'] ? 'Zapisywanie...' : 'Zapisz zdjęcie'}
                                    </button>
                                    <button
                                        onClick={handlePhotoCancelEdit}
                                        className={styles.cancelButton}
                                        disabled={saveLoading['photo']}
                                    >
                                        Anuluj
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <>
                                {directorData.photo_url ? (
                                    <img src={directorData.photo_url} alt={directorData.name} className={styles.directorPhoto} />
                                ) : (
                                    <div className={styles.directorPhotoPlaceholder}>
                                        {directorData.name.charAt(0).toUpperCase()}
                                    </div>
                                )}

                                <button
                                    className={styles.changePhotoButton}
                                    onClick={() => setIsEditingPhoto(true)}
                                    disabled={saveLoading['photo']}
                                >
                                    Zmień zdjęcie
                                </button>
                            </>
                        )}
                    </div>

                    <div className={styles.directorInfo}>
                        <h2>{directorData.name}</h2>
                        <p className={styles.directorBirthDate}>
                            {directorData.birth_date ? formatDate(directorData.birth_date) : 'Brak daty urodzenia'}
                        </p>
                        <p className={styles.directorGender}>{getGenderName(directorData.gender)}</p>
                    </div>
                </div>

                <div className={styles.directorDetailsContent}>
                    <div className={styles.directorDetailsGrid}>
                        {renderEditableField('name', 'Imię i nazwisko')}
                        {renderEditableField('birth_date', 'Data urodzenia', 'date')}
                        {renderEditableField('birth_place', 'Miejsce urodzenia')}

                        <div className={styles.detailItem}>
                            <h3>Płeć:</h3>
                            <div className={styles.genderToggle}>
                                <button
                                    onClick={() => handleGenderChange('M')}
                                    className={`${styles.genderButton} ${directorData.gender === 'M' ? styles.genderButtonActive : ''}`}
                                    disabled={directorData.gender === 'M' || saveLoading['gender']}
                                >
                                    Mężczyzna
                                </button>
                                <button
                                    onClick={() => handleGenderChange('K')}
                                    className={`${styles.genderButton} ${directorData.gender === 'K' ? styles.genderButtonActive : ''}`}
                                    disabled={directorData.gender === 'K' || saveLoading['gender']}
                                >
                                    Kobieta
                                </button>
                                <button
                                    onClick={() => handleGenderChange(null)}
                                    className={`${styles.genderButton} ${directorData.gender === null ? styles.genderButtonActive : ''}`}
                                    disabled={directorData.gender === null || saveLoading['gender']}
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
                            {saveLoading.delete ? 'Usuwanie...' : 'Usuń reżysera'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DirectorsEditPage;

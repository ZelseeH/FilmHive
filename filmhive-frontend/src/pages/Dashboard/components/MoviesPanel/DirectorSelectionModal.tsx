import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import { Director } from '../../services/directorService';
import styles from './DirectorSelectionModal.module.css';

interface DirectorSelectionModalProps {
    visible: boolean;
    onHide: () => void;
    onSelectDirectors: (directorIds: number[]) => Promise<boolean>; // ZMIANA: tablica ID
    excludeDirectorIds?: number[];
}

const DirectorSelectionContent: React.FC<DirectorSelectionModalProps> = ({
    visible,
    onHide,
    onSelectDirectors,
    excludeDirectorIds = []
}) => {
    const [searchTerm, setSearchTerm] = useState<string>('');
    const [selectedDirectors, setSelectedDirectors] = useState<Director[]>([]); // ZMIANA: tablica
    const [submitting, setSubmitting] = useState<boolean>(false);
    const [directors, setDirectors] = useState<Director[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState<number>(1);
    const [hasMore, setHasMore] = useState<boolean>(true);
    const toast = useRef<Toast>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    const fetchDirectors = useCallback(async (searchQuery: string, pageNum: number, reset: boolean = false) => {
        try {
            setLoading(true);
            setError(null);

            let url = `http://localhost:5000/api/directors/?page=${pageNum}&per_page=30&_t=${Date.now()}`;

            if (searchQuery.trim()) {
                url = `http://localhost:5000/api/directors/search?q=${encodeURIComponent(searchQuery)}&page=${pageNum}&per_page=30&_t=${Date.now()}`;
            }

            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });

            if (!response.ok) {
                throw new Error('Nie udało się pobrać reżyserów');
            }

            const data = await response.json();
            const newDirectors = data.directors || [];

            if (reset) {
                setDirectors(newDirectors);
            } else {
                setDirectors(prev => {
                    const existingIds = new Set(prev.map((director: Director) => director.id));
                    const uniqueNewDirectors = newDirectors.filter((director: Director) => !existingIds.has(director.id));
                    return [...prev, ...uniqueNewDirectors];
                });
            }

            setHasMore(pageNum < (data.pagination?.total_pages || 1));
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania reżyserów');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (visible) {
            setDirectors([]);
            setPage(1);
            setHasMore(true);
            setSelectedDirectors([]); // ZMIANA: wyczyść tablicę
            fetchDirectors('', 1, true);
        }
    }, [visible, fetchDirectors]);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setDirectors([]);
            setPage(1);
            setHasMore(true);
            fetchDirectors(searchTerm, 1, true);
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [searchTerm, fetchDirectors]);

    const handleScroll = useCallback(() => {
        if (!scrollRef.current || loading || !hasMore) return;

        const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;

        if (scrollTop + clientHeight >= scrollHeight - 100) {
            const nextPage = page + 1;
            setPage(nextPage);
            fetchDirectors(searchTerm, nextPage, false);
        }
    }, [loading, hasMore, page, searchTerm, fetchDirectors]);

    useEffect(() => {
        const scrollElement = scrollRef.current;
        if (scrollElement) {
            scrollElement.addEventListener('scroll', handleScroll);
            return () => scrollElement.removeEventListener('scroll', handleScroll);
        }
    }, [handleScroll]);

    const availableDirectors = directors.filter(director => !excludeDirectorIds.includes(director.id));

    // ZMIANA: obsługa wielu reżyserów
    const handleDirectorToggle = (director: Director) => {
        setSelectedDirectors(prev => {
            const isSelected = prev.some(selected => selected.id === director.id);

            if (isSelected) {
                // Usuń reżysera z wyboru
                return prev.filter(selected => selected.id !== director.id);
            } else {
                // Dodaj reżysera do wyboru
                return [...prev, director];
            }
        });
    };

    const handleSubmit = async () => {
        if (selectedDirectors.length === 0) {
            toast.current?.show({
                severity: 'warn',
                summary: 'Uwaga',
                detail: 'Wybierz przynajmniej jednego reżysera',
                life: 3000
            });
            return;
        }

        try {
            setSubmitting(true);
            const directorIds = selectedDirectors.map(director => director.id);
            const success = await onSelectDirectors(directorIds);

            if (success) {
                toast.current?.show({
                    severity: 'success',
                    summary: 'Sukces',
                    detail: `Dodano ${selectedDirectors.length} reżyser${selectedDirectors.length === 1 ? 'a' : 'ów'} do filmu`,
                    life: 3000
                });
                onHide();
            }
        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się dodać reżyserów',
                life: 5000
            });
        } finally {
            setSubmitting(false);
        }
    };

    const handleCancel = () => {
        setSelectedDirectors([]);
        setSearchTerm('');
        onHide();
    };

    const isDirectorSelected = (directorId: number) => {
        return selectedDirectors.some(selected => selected.id === directorId);
    };

    const modalHeader = (
        <div className={styles.modalHeader}>
            <h3>Wybierz reżyserów ({selectedDirectors.length} wybranych)</h3>
            <div className={styles.searchContainer}>
                <InputText
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Szukaj reżyserów po nazwie..."
                    className={styles.searchInput}
                />
            </div>
        </div>
    );

    const modalFooter = (
        <div className={styles.modalFooter}>
            <Button
                label="Anuluj"
                icon="pi pi-times"
                onClick={handleCancel}
                className={`p-button-text ${styles.cancelButton}`}
            />
            <Button
                label={submitting ? "Dodawanie..." : `Dodaj ${selectedDirectors.length} reżyser${selectedDirectors.length === 1 ? 'a' : 'ów'}`}
                icon="pi pi-check"
                onClick={handleSubmit}
                disabled={selectedDirectors.length === 0 || submitting}
                loading={submitting}
                className={styles.saveButton}
            />
        </div>
    );

    return (
        <>
            <Toast ref={toast} />
            <Dialog
                visible={visible}
                style={{ width: '75%', maxWidth: '900px' }}
                header={modalHeader}
                footer={modalFooter}
                onHide={handleCancel}
                className={styles.directorModal}
                draggable={false}
                resizable={false}
                contentStyle={{
                    maxHeight: '70vh',
                    overflow: 'hidden',
                    padding: '0',
                    display: 'flex',
                    flexDirection: 'column'
                }}
            >
                <div
                    ref={scrollRef}
                    className={styles.scrollableContent}
                >
                    <div className={styles.modalContent}>
                        {error && (
                            <div className={styles.errorMessage}>
                                {error}
                            </div>
                        )}

                        <div className={styles.directorsGrid}>
                            {availableDirectors.length === 0 && !loading ? (
                                <div className={styles.noResults}>
                                    {searchTerm ?
                                        `Brak reżyserów pasujących do "${searchTerm}"` :
                                        'Wszyscy dostępni reżyserzy są już przypisani do filmu'
                                    }
                                </div>
                            ) : (
                                <>
                                    {availableDirectors.map((director) => (
                                        <div
                                            key={director.id}
                                            className={`${styles.directorCard} ${isDirectorSelected(director.id) ? styles.selected : ''}`}
                                            onClick={() => handleDirectorToggle(director)}
                                        >
                                            <div className={styles.directorCardContent}>
                                                {director.photo_url ? (
                                                    <img
                                                        src={director.photo_url}
                                                        alt={director.name}
                                                        className={styles.directorPhoto}
                                                    />
                                                ) : (
                                                    <div className={styles.directorPhotoPlaceholder}>
                                                        {director.name.charAt(0).toUpperCase()}
                                                    </div>
                                                )}
                                                <div className={styles.directorInfo}>
                                                    <span className={styles.directorName}>
                                                        {director.name}
                                                    </span>
                                                    {director.birth_date && (
                                                        <span className={styles.directorYear}>
                                                            {new Date(director.birth_date).getFullYear()}
                                                        </span>
                                                    )}
                                                    {director.birth_place && (
                                                        <span className={styles.directorPlace}>
                                                            {director.birth_place}
                                                        </span>
                                                    )}
                                                </div>
                                                {isDirectorSelected(director.id) && (
                                                    <div className={styles.selectedBadge}>
                                                        <i className="pi pi-check"></i>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}

                                    {loading && (
                                        <div className={styles.loadingMore}>
                                            <div className={styles.spinner}></div>
                                            <span>Ładowanie więcej reżyserów...</span>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>

                        {selectedDirectors.length > 0 && (
                            <div className={styles.selectedDirectorsSection}>
                                <h4>Wybrani reżyserzy:</h4>
                                <div className={styles.selectedDirectorsList}>
                                    {selectedDirectors.map((director) => (
                                        <div key={director.id} className={styles.selectedDirectorItem}>
                                            <div className={styles.selectedDirectorInfo}>
                                                {director.photo_url ? (
                                                    <img
                                                        src={director.photo_url}
                                                        alt={director.name}
                                                        className={styles.selectedDirectorPhoto}
                                                    />
                                                ) : (
                                                    <div className={styles.selectedDirectorPhotoPlaceholder}>
                                                        {director.name.charAt(0).toUpperCase()}
                                                    </div>
                                                )}
                                                <span className={styles.selectedDirectorName}>
                                                    {director.name}
                                                </span>
                                            </div>
                                            <button
                                                onClick={() => handleDirectorToggle(director)}
                                                className={styles.removeDirectorButton}
                                                type="button"
                                            >
                                                <i className="pi pi-times"></i>
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </Dialog>
        </>
    );
};

const DirectorSelectionModal: React.FC<DirectorSelectionModalProps> = (props) => {
    if (!props.visible) {
        return null;
    }

    return <DirectorSelectionContent {...props} />;
};

export default DirectorSelectionModal;

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import { Actor } from '../../services/actorService';
import styles from './ActorSelectionModal.module.css';

interface SelectedActor {
    actor: Actor;
    role: string;
}

interface ActorSelectionModalProps {
    visible: boolean;
    onHide: () => void;
    onSelectActors: (actors: { actorId: number; role: string }[]) => Promise<boolean>;
    excludeActorIds?: number[];
}

const ActorSelectionContent: React.FC<ActorSelectionModalProps> = ({
    visible,
    onHide,
    onSelectActors,
    excludeActorIds = []
}) => {
    const [searchTerm, setSearchTerm] = useState<string>('');
    const [selectedActors, setSelectedActors] = useState<SelectedActor[]>([]);
    const [submitting, setSubmitting] = useState<boolean>(false);
    const [actors, setActors] = useState<Actor[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState<number>(1);
    const [hasMore, setHasMore] = useState<boolean>(true);
    const toast = useRef<Toast>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    const fetchActors = useCallback(async (searchQuery: string, pageNum: number, reset: boolean = false) => {
        try {
            setLoading(true);
            setError(null);

            let url = `http://localhost:5000/api/actors/filter?page=${pageNum}&per_page=30&sort_by=name&sort_order=asc&_t=${Date.now()}`;

            if (searchQuery.trim()) {
                url += `&name=${encodeURIComponent(searchQuery)}`;
            }

            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });

            if (!response.ok) {
                throw new Error('Nie udało się pobrać aktorów');
            }

            const data = await response.json();
            const newActors = data.actors || [];

            if (reset) {
                setActors(newActors);
            } else {
                // Filtruj duplikaty
                setActors(prev => {
                    const existingIds = new Set(prev.map((actor: Actor) => actor.id));
                    const uniqueNewActors = newActors.filter((actor: Actor) => !existingIds.has(actor.id));
                    return [...prev, ...uniqueNewActors];
                });
            }

            setHasMore(pageNum < (data.pagination?.total_pages || 1));
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas pobierania aktorów');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (visible) {
            setActors([]);
            setPage(1);
            setHasMore(true);
            setSelectedActors([]);
            fetchActors('', 1, true);
        }
    }, [visible, fetchActors]);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setActors([]);
            setPage(1);
            setHasMore(true);
            fetchActors(searchTerm, 1, true);
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [searchTerm, fetchActors]);

    // Infinite scroll
    const handleScroll = useCallback(() => {
        if (!scrollRef.current || loading || !hasMore) return;

        const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;

        if (scrollTop + clientHeight >= scrollHeight - 100) {
            const nextPage = page + 1;
            setPage(nextPage);
            fetchActors(searchTerm, nextPage, false);
        }
    }, [loading, hasMore, page, searchTerm, fetchActors]);

    useEffect(() => {
        const scrollElement = scrollRef.current;
        if (scrollElement) {
            scrollElement.addEventListener('scroll', handleScroll);
            return () => scrollElement.removeEventListener('scroll', handleScroll);
        }
    }, [handleScroll]);

    const availableActors = actors.filter(actor => !excludeActorIds.includes(actor.id));

    const handleActorToggle = (actor: Actor) => {
        setSelectedActors(prev => {
            const isSelected = prev.some(selected => selected.actor.id === actor.id);

            if (isSelected) {
                return prev.filter(selected => selected.actor.id !== actor.id);
            } else {
                return [...prev, { actor, role: '' }];
            }
        });
    };

    const handleRoleChange = (actorId: number, role: string) => {
        setSelectedActors(prev =>
            prev.map(selected =>
                selected.actor.id === actorId
                    ? { ...selected, role }
                    : selected
            )
        );
    };

    const handleSubmit = async () => {
        if (selectedActors.length === 0) {
            toast.current?.show({
                severity: 'warn',
                summary: 'Uwaga',
                detail: 'Wybierz przynajmniej jednego aktora',
                life: 3000
            });
            return;
        }

        try {
            setSubmitting(true);
            const actorsToAdd = selectedActors.map(selected => ({
                actorId: selected.actor.id,
                role: selected.role.trim()
            }));

            const success = await onSelectActors(actorsToAdd);

            if (success) {
                toast.current?.show({
                    severity: 'success',
                    summary: 'Sukces',
                    detail: `Dodano ${selectedActors.length} aktor${selectedActors.length === 1 ? 'a' : 'ów'} do filmu`,
                    life: 3000
                });
                onHide();
            }
        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się dodać aktorów',
                life: 5000
            });
        } finally {
            setSubmitting(false);
        }
    };

    const handleCancel = () => {
        setSelectedActors([]);
        setSearchTerm('');
        onHide();
    };

    const isActorSelected = (actorId: number) => {
        return selectedActors.some(selected => selected.actor.id === actorId);
    };

    const modalHeader = (
        <div className={styles.modalHeader}>
            <h3>Wybierz aktorów ({selectedActors.length} wybranych)</h3>
            <div className={styles.searchContainer}>
                <InputText
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Szukaj aktorów po nazwie..."
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
                label={submitting ? "Dodawanie..." : `Dodaj ${selectedActors.length} aktor${selectedActors.length === 1 ? 'a' : 'ów'}`}
                icon="pi pi-check"
                onClick={handleSubmit}
                disabled={selectedActors.length === 0 || submitting}
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
                style={{ width: '85%', maxWidth: '1200px' }}
                header={modalHeader}
                footer={modalFooter}
                onHide={handleCancel}
                className={styles.actorModal}
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

                        <div className={styles.actorsGrid}>
                            {availableActors.length === 0 && !loading ? (
                                <div className={styles.noResults}>
                                    {searchTerm ?
                                        `Brak aktorów pasujących do "${searchTerm}"` :
                                        'Wszyscy dostępni aktorzy są już przypisani do filmu'
                                    }
                                </div>
                            ) : (
                                <>
                                    {availableActors.map((actor) => (
                                        <div
                                            key={actor.id}
                                            className={`${styles.actorCard} ${isActorSelected(actor.id) ? styles.selected : ''}`}
                                            onClick={() => handleActorToggle(actor)}
                                        >
                                            <div className={styles.actorCardContent}>
                                                {actor.photo_url ? (
                                                    <img
                                                        src={actor.photo_url}
                                                        alt={actor.name}
                                                        className={styles.actorPhoto}
                                                    />
                                                ) : (
                                                    <div className={styles.actorPhotoPlaceholder}>
                                                        {actor.name.charAt(0).toUpperCase()}
                                                    </div>
                                                )}
                                                <div className={styles.actorInfo}>
                                                    <span className={styles.actorName}>
                                                        {actor.name}
                                                    </span>
                                                    {actor.birth_date && (
                                                        <span className={styles.actorYear}>
                                                            {new Date(actor.birth_date).getFullYear()}
                                                        </span>
                                                    )}
                                                    {actor.birth_place && (
                                                        <span className={styles.actorPlace}>
                                                            {actor.birth_place}
                                                        </span>
                                                    )}
                                                </div>
                                                {isActorSelected(actor.id) && (
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
                                            <span>Ładowanie więcej aktorów...</span>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>

                        {selectedActors.length > 0 && (
                            <div className={styles.selectedActorsSection}>
                                <h4>Wybrani aktorzy i ich role:</h4>
                                <div className={styles.selectedActorsList}>
                                    {selectedActors.map((selected) => (
                                        <div key={selected.actor.id} className={styles.selectedActorItem}>
                                            <div className={styles.selectedActorInfo}>
                                                {selected.actor.photo_url ? (
                                                    <img
                                                        src={selected.actor.photo_url}
                                                        alt={selected.actor.name}
                                                        className={styles.selectedActorPhoto}
                                                    />
                                                ) : (
                                                    <div className={styles.selectedActorPhotoPlaceholder}>
                                                        {selected.actor.name.charAt(0).toUpperCase()}
                                                    </div>
                                                )}
                                                <span className={styles.selectedActorName}>
                                                    {selected.actor.name}
                                                </span>
                                            </div>
                                            <div className={styles.roleInputContainer}>
                                                <InputText
                                                    value={selected.role}
                                                    onChange={(e) => handleRoleChange(selected.actor.id, e.target.value)}
                                                    placeholder="Rola w filmie (opcjonalne)"
                                                    className={styles.roleInput}
                                                    maxLength={100}
                                                />
                                            </div>
                                            <button
                                                onClick={() => handleActorToggle(selected.actor)}
                                                className={styles.removeActorButton}
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

const ActorSelectionModal: React.FC<ActorSelectionModalProps> = (props) => {
    if (!props.visible) {
        return null;
    }

    return <ActorSelectionContent {...props} />;
};

export default ActorSelectionModal;

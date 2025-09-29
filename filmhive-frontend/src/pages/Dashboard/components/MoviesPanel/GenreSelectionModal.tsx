import React, { useState, useRef, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import { Genre } from '../../services/genresService';
import styles from './GenreSelectionModal.module.css';

interface GenreSelectionModalProps {
    visible: boolean;
    onHide: () => void;
    onSelectGenres: (genreIds: number[]) => Promise<boolean>;
    excludeGenreIds?: number[];
}

const GenreSelectionContent: React.FC<GenreSelectionModalProps> = ({
    visible,
    onHide,
    onSelectGenres,
    excludeGenreIds = []
}) => {
    const [selectedGenres, setSelectedGenres] = useState<Genre[]>([]);
    const [submitting, setSubmitting] = useState<boolean>(false);
    const [genres, setGenres] = useState<Genre[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const toast = useRef<Toast>(null);

    useEffect(() => {
        if (visible) {
            const fetchAllGenres = async () => {
                setLoading(true);
                setError(null);
                try {
                    const response = await fetch('http://localhost:5000/api/genres?_t=' + Date.now());
                    if (!response.ok) {
                        throw new Error('Nie udało się pobrać gatunków');
                    }
                    const data = await response.json();
                    setGenres(Array.isArray(data) ? data : data.genres || []);
                } catch (e: any) {
                    setError(e.message || 'Wystąpił błąd podczas pobierania gatunków');
                } finally {
                    setLoading(false);
                }
            };
            fetchAllGenres();
            setSelectedGenres([]);
        }
    }, [visible]);

    const availableGenres = genres.filter(genre => !excludeGenreIds.includes(genre.id));

    const handleGenreToggle = (genre: Genre) => {
        setSelectedGenres(prev => {
            const isSelected = prev.some(selected => selected.id === genre.id);
            if (isSelected) {
                return prev.filter(selected => selected.id !== genre.id);
            } else {
                return [...prev, genre];
            }
        });
    };

    const isGenreSelected = (genreId: number) => {
        return selectedGenres.some(selected => selected.id === genreId);
    };

    const handleSubmit = async () => {
        if (selectedGenres.length === 0) {
            toast.current?.show({
                severity: 'warn',
                summary: 'Uwaga',
                detail: 'Wybierz przynajmniej jeden gatunek',
                life: 3000
            });
            return;
        }

        try {
            setSubmitting(true);
            const genreIds = selectedGenres.map(genre => genre.id);
            const success = await onSelectGenres(genreIds);
            if (success) {
                toast.current?.show({
                    severity: 'success',
                    summary: 'Sukces',
                    detail: `Dodano ${selectedGenres.length} gatunek${selectedGenres.length === 1 ? '' : 'ów'} do filmu`,
                    life: 3000
                });
                onHide();
            }
        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się dodać gatunków',
                life: 5000
            });
        } finally {
            setSubmitting(false);
        }
    };

    const handleCancel = () => {
        setSelectedGenres([]);
        onHide();
    };

    // Funkcja pomocnicza do wyboru ikony
    const getGenreIcon = (genreName: string): string => {
        const name = genreName.toLowerCase();

        // Dokładne dopasowania
        if (name === 'akcja') return '🎬';
        if (name === 'animacja') return '🎨';
        if (name === 'animacja dla dorosłych') return '🔞';
        if (name === 'anime') return '🎌';
        if (name === 'baśń') return '🧚';
        if (name === 'biograficzny') return '📖';
        if (name === 'czarna komedia') return '🖤';
        if (name === 'dla dzieci') return '👶';
        if (name === 'dla młodzieży') return '🧒';
        if (name === 'dokumentalizowany') return '📽️';
        if (name === 'dokumentalny') return '📹';
        if (name === 'dramat') return '🎭';
        if (name === 'dramat historyczny') return '⚔️';
        if (name === 'dramat obyczajowy') return '👥';
        if (name === 'dramat sądowy') return '⚖️';
        if (name === 'dreszczowiec') return '😱';
        if (name === 'erotyczny') return '💋';
        if (name === 'familijny') return '👨‍👩‍👧‍👦';
        if (name === 'fantasy') return '🧙';
        if (name === 'film-noir') return '🕵️‍♂️';
        if (name === 'groteska filmowa') return '🎪';
        if (name === 'historyczny') return '🏛️';
        if (name === 'horror') return '👻';
        if (name === 'katastroficzny') return '🌪️';
        if (name === 'komedia') return '😂';
        if (name === 'komedia kryminalna') return '🤡';
        if (name === 'komedia rom.' || name === 'komedia romantyczna') return '💕';
        if (name === 'gangsterski') return '🔫';
        if (name === 'thriller') return '🔪';
        if (name.includes('akcja')) return '💥';
        if (name.includes('przygod')) return '🗺️';
        if (name.includes('wojenn')) return '⚔️';
        if (name.includes('western')) return '🤠';
        if (name.includes('musical')) return '🎵';
        if (name.includes('sport')) return '⚽';
        if (name.includes('komedia')) return '😂';
        if (name.includes('dramat')) return '🎭';
        if (name.includes('krymin')) return '🔍';
        if (name.includes('sci-fi') || name.includes('science')) return '🚀';
        if (name.includes('fantasy') || name.includes('fantast')) return '🧙‍♂️';
        if (name.includes('horror') || name.includes('straszen')) return '👻';
        if (name.includes('romans') || name.includes('miłosn')) return '💝';
        if (name.includes('dokument')) return '📹';
        if (name.includes('animacj')) return '🎨';
        if (name.includes('dla dzieci') || name.includes('dziecięc')) return '👶';
        if (name.includes('młodzież')) return '🧒';
        if (name.includes('rodzinn') || name.includes('family')) return '👨‍👩‍👧‍👦';
        if (name.includes('biograf')) return '👤';
        if (name.includes('historia') || name.includes('histor')) return '🏛️';
        if (name.includes('noir')) return '🕵️‍♀️';
        if (name.includes('gangster') || name.includes('mafi')) return '🔫';
        if (name.includes('katastro')) return '🌪️';
        if (name.includes('erotycz') || name.includes('sex')) return '💋';
        if (name.includes('religious') || name.includes('religijn')) return '⛪';
        if (name.includes('poezj') || name.includes('poetry')) return '📝';
        if (name.includes('surreal')) return '🌀';
        if (name.includes('experimental')) return '🔬';
        if (name.includes('minimalist')) return '⚪';

        return '🎬';
    };

    const modalHeader = (
        <div className={styles.modalHeader}>
            <h3>Wybierz gatunki ({selectedGenres.length} wybranych)</h3>
        </div>
    );

    const modalFooter = (
        <div className={styles.modalFooter}>
            <Button
                label="Anuluj"
                icon="pi pi-times"
                onClick={handleCancel}
                className="p-button-text"
            />
            <Button
                label={submitting ? "Dodawanie..." : `Dodaj ${selectedGenres.length} gatunek${selectedGenres.length === 1 ? '' : 'ów'}`}
                icon="pi pi-check"
                onClick={handleSubmit}
                disabled={selectedGenres.length === 0 || submitting}
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
                style={{ width: '70%', maxWidth: '700px' }}
                header={modalHeader}
                footer={modalFooter}
                onHide={handleCancel}
                className={styles.genreModal}
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
                <div className={styles.scrollableContent}>
                    <div className={styles.modalContent}>
                        {error && (
                            <div className={styles.errorMessage}>
                                {error}
                            </div>
                        )}

                        <div className={styles.genresGrid}>
                            {availableGenres.length === 0 && !loading ? (
                                <div className={styles.noResults}>
                                    Wszystkie dostępne gatunki są już przypisane do filmu
                                </div>
                            ) : (
                                <>
                                    {availableGenres.map((genre) => (
                                        <div
                                            key={genre.id}
                                            className={`${styles.genreCard} ${isGenreSelected(genre.id) ? styles.selected : ''}`}
                                            onClick={() => handleGenreToggle(genre)}
                                        >
                                            <div className={styles.genreCardContent}>
                                                <div className={styles.genreIcon}>
                                                    {getGenreIcon(genre.name)}
                                                </div>
                                                <div className={styles.genreInfo}>
                                                    <span className={styles.genreName}>
                                                        {genre.name}
                                                    </span>
                                                </div>
                                                {isGenreSelected(genre.id) && (
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
                                            <span>Ładowanie gatunków...</span>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>

                        {selectedGenres.length > 0 && (
                            <div className={styles.selectedGenresSection}>
                                <h4>Wybrane gatunki:</h4>
                                <div className={styles.selectedGenresList}>
                                    {selectedGenres.map((genre) => (
                                        <div key={genre.id} className={styles.selectedGenreItem}>
                                            <div className={styles.selectedGenreInfo}>
                                                <span className={styles.selectedGenreIcon}>
                                                    {getGenreIcon(genre.name)}
                                                </span>
                                                <span className={styles.selectedGenreName}>
                                                    {genre.name}
                                                </span>
                                            </div>
                                            <button
                                                onClick={() => handleGenreToggle(genre)}
                                                className={styles.removeGenreButton}
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

const GenreSelectionModal: React.FC<GenreSelectionModalProps> = (props) => {
    if (!props.visible) {
        return null;
    }

    return <GenreSelectionContent {...props} />;
};

export default GenreSelectionModal;

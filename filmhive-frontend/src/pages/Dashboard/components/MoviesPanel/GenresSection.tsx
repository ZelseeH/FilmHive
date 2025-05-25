import React from 'react';
import GenreSelectionModal from './GenreSelectionModal';
import styles from './GenresSection.module.css';

interface Genre {
    id: number;
    name: string;
}

interface GenresSectionProps {
    genres: Genre[];
    onRemoveGenre: (genreId: number) => Promise<void>;
    onAddGenres: (genreIds: number[]) => Promise<boolean>;
    relationsLoading: boolean;
}

const GenresSection: React.FC<GenresSectionProps> = ({
    genres,
    onRemoveGenre,
    onAddGenres,
    relationsLoading
}) => {
    const [showGenreModal, setShowGenreModal] = React.useState(false);

    return (
        <div className={styles.relationsSection}>
            <div className={styles.sectionHeader}>
                <h3>Gatunki ({genres?.length || 0})</h3>
                <button
                    className={styles.addButton}
                    onClick={() => setShowGenreModal(true)}
                >
                    + Dodaj
                </button>
            </div>

            <div className={styles.genresGrid}>
                {genres?.map((genre) => (
                    <div key={genre.id} className={styles.genreCard}>
                        <button
                            onClick={() => onRemoveGenre(genre.id)}
                            className={styles.removeButton}
                            disabled={relationsLoading}
                        >
                            ×
                        </button>

                        <div className={styles.genreInfo}>
                            <div className={styles.genreIcon}>
                                {getGenreIcon(genre.name)}
                            </div>
                            <span className={styles.genreName}>{genre.name}</span>
                        </div>
                    </div>
                ))}
            </div>

            <GenreSelectionModal
                visible={showGenreModal}
                onHide={() => setShowGenreModal(false)}
                onSelectGenres={onAddGenres}
                excludeGenreIds={genres?.map((genre) => genre.id) || []}
            />
        </div>
    );
};

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

    // Fallback dla nieznanych gatunków
    return '🎬';
};
export default GenresSection;

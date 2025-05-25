import React from 'react';
import DirectorSelectionModal from './DirectorSelectionModal';
import styles from './DirectorsSection.module.css';

interface Director {
    id: number;
    name: string;
    photo_url?: string;
}

interface DirectorsSectionProps {
    directors: Director[];
    onRemoveDirector: (directorId: number) => Promise<void>;
    onAddDirectors: (directorIds: number[]) => Promise<boolean>; // ZMIANA: onAddDirectors
    relationsLoading: boolean;
}

const DirectorsSection: React.FC<DirectorsSectionProps> = ({
    directors,
    onRemoveDirector,
    onAddDirectors, // ZMIANA: onAddDirectors
    relationsLoading
}) => {
    const [showDirectorModal, setShowDirectorModal] = React.useState(false);

    return (
        <div className={styles.relationsSection}>
            <div className={styles.sectionHeader}>
                <h3>Reżyserzy ({directors?.length || 0})</h3>
                <button
                    className={styles.addButton}
                    onClick={() => setShowDirectorModal(true)}
                >
                    + Dodaj
                </button>
            </div>

            <div className={styles.directorsGrid}>
                {directors?.map((director) => (
                    <div key={director.id} className={styles.directorCard}>
                        <button
                            onClick={() => onRemoveDirector(director.id)}
                            className={styles.removeButton}
                            disabled={relationsLoading}
                        >
                            ×
                        </button>

                        <div className={styles.directorInfo}>
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
                            <span className={styles.directorName}>{director.name}</span>
                        </div>
                    </div>
                ))}
            </div>

            <DirectorSelectionModal
                visible={showDirectorModal}
                onHide={() => setShowDirectorModal(false)}
                onSelectDirectors={onAddDirectors} // ZMIANA: używamy onAddDirectors
                excludeDirectorIds={directors?.map((director) => director.id) || []}
            />
        </div>
    );
};

export default DirectorsSection;

import React from 'react';
import { MovieActor } from '../../services/movieRelationsService';
import ActorSelectionModal from './ActorSelectionModal';
import styles from './ActorsSection.module.css';

interface ActorsSectionProps {
    actors: MovieActor[];
    onRemoveActor: (actorId: number) => Promise<void>;
    onAddActors: (actors: { actorId: number; role: string }[]) => Promise<boolean>;
    relationsLoading: boolean;
}

const ActorsSection: React.FC<ActorsSectionProps> = ({
    actors,
    onRemoveActor,
    onAddActors,
    relationsLoading
}) => {
    const [showActorModal, setShowActorModal] = React.useState(false);

    return (
        <div className={styles.relationsSection}>
            <div className={styles.sectionHeader}>
                <h3>Aktorzy ({actors?.length || 0})</h3>
                <button
                    className={styles.addButton}
                    onClick={() => setShowActorModal(true)}
                >
                    + Dodaj
                </button>
            </div>

            <div className={styles.actorsGrid}>
                {actors?.map((actor) => (
                    <div key={actor.id} className={styles.actorCard}>
                        <button
                            onClick={() => onRemoveActor(actor.id)}
                            className={styles.removeButton}
                            disabled={relationsLoading}
                        >
                            ×
                        </button>

                        <div className={styles.actorInfo}>
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
                            <span className={styles.actorName}>{actor.name}</span>
                            {actor.role && (
                                <span className={styles.actorRole}>{actor.role}</span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            <ActorSelectionModal
                visible={showActorModal}
                onHide={() => setShowActorModal(false)}
                onSelectActors={onAddActors}
                excludeActorIds={actors?.map((actor) => actor.id) || []}
            />
        </div>
    );
};

export default ActorsSection;

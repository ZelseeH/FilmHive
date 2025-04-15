// src/features/actors/components/ActorHeaderSection/ActorHeaderSection.tsx
import React from 'react';
import { Actor } from '../../services/actorService';
import { handleActorImageError, formatActorBirthDate, calculateAge } from '../../utils/actorUtils';
import styles from './ActorHeaderSection.module.css';

interface ActorHeaderSectionProps {
    actor: Actor;
    onShowFullBio: () => void;
}

const ActorHeaderSection: React.FC<ActorHeaderSectionProps> = ({ actor, onShowFullBio }) => {
    return (
        <div className={styles['actor-header-section']}>
            <div className={styles['actor-photo']}>
                <img
                    src={actor.photo_url || '/placeholder-actor.jpg'}
                    alt={`Zdjęcie aktora ${actor.name}`}
                    onError={(e) => handleActorImageError(e)}
                />
            </div>
            <div className={styles['actor-header-info']}>
                <h1 className={styles['actor-name']}>{actor.name}</h1>

                <div className={styles['actor-details']}>
                    {actor.birth_date && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>Data urodzenia:</span>
                            <span className={styles['detail-value']}>{formatActorBirthDate(actor.birth_date)}</span>
                        </div>
                    )}

                    {actor.birth_place && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>Miejsce urodzenia:</span>
                            <span className={styles['detail-value']}>{actor.birth_place}</span>
                        </div>
                    )}

                    {actor.birth_date && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>Wiek:</span>
                            <span className={styles['detail-value']}>{calculateAge(actor.birth_date)} lat</span>
                        </div>
                    )}

                    {actor.gender && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>Płeć:</span>
                            <span className={styles['detail-value']}>{actor.gender === 'M' ? 'Mężczyzna' : 'Kobieta'}</span>
                        </div>
                    )}
                </div>

                <div className={styles['actor-bio-container']}>
                    <p className={styles['actor-bio']}>
                        {actor.biography && actor.biography.length > 300
                            ? `${actor.biography.substring(0, 300)}...`
                            : actor.biography || 'Brak dostępnej biografii.'}
                    </p>
                    {actor.biography && actor.biography.length > 300 && (
                        <button
                            className={styles['show-full-bio-btn']}
                            onClick={onShowFullBio}
                        >
                            zobacz pełną biografię
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ActorHeaderSection;

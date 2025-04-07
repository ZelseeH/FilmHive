import React from 'react';
import { Link } from 'react-router-dom';
import { Actor } from '../../../services/actorService';
import { getActorInitials, getActorSlug } from '../../../utils/actorUtils';
import styles from './ActorItem.module.css';

interface ActorItemProps {
    actor: Actor;
}

const ActorItem: React.FC<ActorItemProps> = ({ actor }) => {
    // Obliczanie wieku aktora
    const calculateAge = () => {
        if (!actor.birth_date) return null;

        const birthDate = new Date(actor.birth_date);
        const birthYear = birthDate.getFullYear();
        const currentYear = new Date().getFullYear();
        const age = currentYear - birthYear;

        return { age, birthYear };
    };

    const ageInfo = calculateAge();

    return (
        <div className={styles.actorItem}>
            <div className={styles.actorPhoto}>
                <Link to={`/actor/details/${getActorSlug(actor.name)}`} state={{ actorId: actor.id }}>
                    {actor.photo_url ? (
                        <img src={actor.photo_url} alt={actor.name} />
                    ) : (
                        <div className={styles.noImage}>{getActorInitials(actor.name)}</div>
                    )}
                </Link>
            </div>
            <div className={styles.actorInfo}>
                <div className={styles.actorLabel}>AKTOR</div>
                <div className={styles.actorHeader}>
                    <h3 className={styles.actorName}>
                        <Link to={`/actor/details/${getActorSlug(actor.name)}`} state={{ actorId: actor.id }}>
                            {actor.name}
                        </Link>
                    </h3>
                    {ageInfo && (
                        <p className={styles.actorAge}>
                            {ageInfo.age} lat ({ageInfo.birthYear})
                        </p>
                    )}
                </div>
                <div className={styles.actorDetails}>
                    {actor.birth_place && (
                        <p className={styles.actorBirthPlace}>
                            <span>Miejsce Urodzenia</span>
                            <span className={styles.birthPlaceText}>{actor.birth_place}</span>
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ActorItem;

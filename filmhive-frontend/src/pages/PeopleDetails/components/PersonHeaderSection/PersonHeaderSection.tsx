import React, { useState } from 'react';
import { Person } from '../../services/peopleService';
import { handlePersonImageError, formatPersonBirthDate, calculateAge } from '../../utils/personUtils';
import styles from './PersonHeaderSection.module.css';

interface PersonHeaderSectionProps {
    person: Person;
    onShowFullBio: () => void;
}

const PersonHeaderSection: React.FC<PersonHeaderSectionProps> = ({ person, onShowFullBio }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    const getPersonTypeLabel = (type: 'actor' | 'director', gender?: string | null): string =>
        type === 'actor' ? (gender === 'K' ? 'Aktorka' : 'Aktor') : (gender === 'K' ? 'Reżyserka' : 'Reżyser');

    const personTypeLabel = getPersonTypeLabel(person.type, person.gender);

    // ✨ JavaScript truncation jako backup
    const MAX_CHARS = 400;
    const biography = person.biography || '';
    const shouldTruncate = biography.length > MAX_CHARS;
    const displayBio = isExpanded || !shouldTruncate
        ? biography
        : `${biography.substring(0, MAX_CHARS).trim()}...`;

    return (
        <div className={styles['person-header-section']}>
            <div className={styles['person-photo']}>
                {person.photo_url ? (
                    <img
                        src={person.photo_url}
                        alt={person.name}
                        onError={(e) => handlePersonImageError(e)}
                    />
                ) : (
                    <div className={styles['no-image']}>
                        {person.name && person.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </div>
                )}
            </div>

            <div className={styles['person-header-info']}>
                <div className={styles['person-type-label']}>{personTypeLabel}</div>
                <h1 className={styles['person-name']}>{person.name}</h1>

                <div className={styles['person-details']}>
                    {person.birth_date && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>Data urodzenia:</span>
                            <span className={styles['detail-value']}>{formatPersonBirthDate(person.birth_date)}</span>
                        </div>
                    )}
                    {person.birth_place && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>Miejsce urodzenia:</span>
                            <span className={styles['detail-value']}>{person.birth_place}</span>
                        </div>
                    )}
                    {person.birth_date && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>Wiek:</span>
                            <span className={styles['detail-value']}>{calculateAge(person.birth_date)} lat</span>
                        </div>
                    )}
                    {person.gender && (
                        <div className={styles['detail-item']}>
                            <span className={styles['detail-label']}>Płeć:</span>
                            <span className={styles['detail-value']}>{person.gender === 'M' ? 'Mężczyzna' : 'Kobieta'}</span>
                        </div>
                    )}
                </div>

                {/* ✨ POŁĄCZENIE: JavaScript truncation + CSS jako backup */}
                <div className={styles['person-bio-container']}>
                    <p className={`${styles['person-bio']} ${isExpanded ? styles['expanded'] : ''}`}>
                        {displayBio || 'Brak dostępnej biografii.'}
                    </p>
                    {shouldTruncate && (
                        <div className={styles['bio-buttons']}>
                            <button
                                className={styles['show-full-bio-btn']}
                                onClick={() => setIsExpanded(!isExpanded)}
                            >
                                {isExpanded ? 'zwiń opis' : 'zobacz pełny opis'}
                            </button>
                            <button
                                className={styles['modal-bio-btn']}
                                onClick={onShowFullBio}
                            >
                                otwórz w oknie
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PersonHeaderSection;

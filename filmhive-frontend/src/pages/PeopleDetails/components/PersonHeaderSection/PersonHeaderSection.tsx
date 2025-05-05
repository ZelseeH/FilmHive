// src/features/people/components/PersonHeaderSection/PersonHeaderSection.tsx
import React from 'react';
import { Person } from '../../services/peopleService';
import { handlePersonImageError, formatPersonBirthDate, calculateAge, getPersonTypeLabel } from '../../utils/personUtils';
import styles from './PersonHeaderSection.module.css';

interface PersonHeaderSectionProps {
    person: Person;
    onShowFullBio: () => void;
}

const PersonHeaderSection: React.FC<PersonHeaderSectionProps> = ({ person, onShowFullBio }) => {
    const personTypeLabel = getPersonTypeLabel(person.type);

    return (
        <div className={styles['person-header-section']}>
            <div className={styles['person-photo']}>
                <img
                    src={person.photo_url || `/placeholder-${person.type}.jpg`}
                    alt={`Zdjęcie - ${person.name}`}
                    onError={(e) => handlePersonImageError(e, person.type)}
                />
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

                <div className={styles['person-bio-container']}>
                    <p className={styles['person-bio']}>
                        {person.biography && person.biography.length > 300
                            ? `${person.biography.substring(0, 300)}...`
                            : person.biography || 'Brak dostępnej biografii.'}
                    </p>
                    {person.biography && person.biography.length > 300 && (
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

export default PersonHeaderSection;

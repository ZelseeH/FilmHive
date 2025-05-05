import React from 'react';
import { Link } from 'react-router-dom';
import { Person } from '../services/peopleService';
import { getPersonInitials, getPersonSlug, getPersonTypeLabel } from '../utils/personUtils';
import styles from './PeopleItem.module.css';

interface PersonItemProps {
    person: Person;
}

const PersonItem: React.FC<PersonItemProps> = ({ person }) => {
    const calculateAge = () => {
        if (!person.birth_date) return null;

        const birthDate = new Date(person.birth_date);
        const birthYear = birthDate.getFullYear();
        const currentYear = new Date().getFullYear();
        const age = currentYear - birthYear;

        return { age, birthYear };
    };

    const ageInfo = calculateAge();
    const personTypeLabel = getPersonTypeLabel(person.type);

    return (
        <div className={styles.personItem}>
            <div className={styles.personPhoto}>
                <Link to={`/people/${person.type}/${getPersonSlug(person.name)}`} state={{ personId: person.id, personType: person.type }}>
                    {person.photo_url ? (
                        <img
                            src={person.photo_url}
                            alt={person.name}
                            onError={(e) => {
                                const target = e.target as HTMLImageElement;
                                target.src = person.type === 'actor' ? '/placeholder-actor.jpg' : '/placeholder-director.jpg';
                            }}
                        />
                    ) : (
                        <div className={styles.noImage}>{getPersonInitials(person.name)}</div>
                    )}
                </Link>
            </div>
            <div className={styles.personInfo}>
                <div className={styles.personLabel}>{personTypeLabel.toUpperCase()}</div>
                <div className={styles.personHeader}>
                    <h3 className={styles.personName}>
                        <Link to={`/people/${person.type}/${getPersonSlug(person.name)}`} state={{ personId: person.id, personType: person.type }}>
                            {person.name}
                        </Link>
                    </h3>
                    {ageInfo && (
                        <p className={styles.personAge}>
                            {ageInfo.age} lat ({ageInfo.birthYear})
                        </p>
                    )}
                </div>
                <div className={styles.personDetails}>
                    {person.birth_place && (
                        <p className={styles.personBirthPlace}>
                            <span>Miejsce Urodzenia</span>
                            <span className={styles.birthPlaceText}>{person.birth_place}</span>
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PersonItem;

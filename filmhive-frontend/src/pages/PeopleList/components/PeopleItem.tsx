import React from 'react';
import { Link } from 'react-router-dom';
import { Person } from '../services/peopleService';
import { getPersonInitials, getPersonSlug } from '../utils/peopleUtils';
import styles from './PeopleItem.module.css';

interface PeopleItemProps {
    person: Person;
}

const PeopleItem: React.FC<PeopleItemProps> = ({ person }) => {
    const calculateAge = () => {
        if (!person.birth_date) return null;

        const birthDate = new Date(person.birth_date);
        const birthYear = birthDate.getFullYear();
        const currentYear = new Date().getFullYear();
        const age = currentYear - birthYear;

        return { age, birthYear };
    };

    const ageInfo = calculateAge();

    // Dynamiczne etykiety i ścieżki
    const label = person.type === 'director' ? 'REŻYSER' : 'AKTOR';
    const detailsPath = person.type === 'director'
        ? `/director/details/${getPersonSlug(person.name)}`
        : `/actor/details/${getPersonSlug(person.name)}`;

    return (
        <div className={styles.peopleItem}>
            <div className={styles.peoplePhoto}>
                <Link to={detailsPath} state={{ personId: person.id }}>
                    {person.photo_url ? (
                        <img src={person.photo_url} alt={person.name} />
                    ) : (
                        <div className={styles.noImage}>{getPersonInitials(person.name)}</div>
                    )}
                </Link>
            </div>
            <div className={styles.peopleInfo}>
                <div className={styles.peopleLabel}>{label}</div>
                <div className={styles.peopleHeader}>
                    <h3 className={styles.peopleName}>
                        <Link to={detailsPath} state={{ personId: person.id }}>
                            {person.name}
                        </Link>
                    </h3>
                    {ageInfo && (
                        <p className={styles.peopleAge}>
                            {ageInfo.age} lat ({ageInfo.birthYear})
                        </p>
                    )}
                </div>
                <div className={styles.peopleDetails}>
                    {person.birth_place && (
                        <p className={styles.peopleBirthPlace}>
                            <span>Miejsce Urodzenia</span>
                            <span className={styles.birthPlaceText}>{person.birth_place}</span>
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PeopleItem;

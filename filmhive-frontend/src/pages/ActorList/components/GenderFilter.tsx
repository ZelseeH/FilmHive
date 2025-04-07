import React from 'react';
import styles from './FilterOptions.module.css';

interface Gender {
    value: string;
    label: string;
}

interface GenderFilterProps {
    genders: Gender[];
    selectedGender: string;
    onToggle: (gender: string) => void;
}

const GenderFilter: React.FC<GenderFilterProps> = ({ genders, selectedGender, onToggle }) => {
    return (
        <div className={styles.filterSection}>
            <h3>Płeć</h3>
            <div className={styles.filterOptions}>
                {genders.map(gender => (
                    <button
                        key={gender.value}
                        className={`${styles.filterOption} ${selectedGender === gender.value ? styles.selected : ''}`}
                        onClick={() => onToggle(gender.value)}
                    >
                        {gender.label}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default GenderFilter;

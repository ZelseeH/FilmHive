import React from 'react';
import styles from './FilterOptions.module.css';

interface CountryFilterProps {
    countries: string[];
    selectedCountries: string[];
    isLoading: boolean;
    onToggle: (country: string) => void;
}

const CountryFilter: React.FC<CountryFilterProps> = ({ countries, selectedCountries, isLoading, onToggle }) => {
    return (
        <div className={styles.filterSection}>
            <h3>Miejsce urodzenia</h3>
            {isLoading ? (
                <div className={styles.loading}>Ładowanie miejsc...</div>
            ) : (
                <div className={styles.filterOptions}>
                    {countries.map(country => (
                        <button
                            key={country}
                            className={`${styles.filterOption} ${selectedCountries.includes(country) ? styles.selected : ''}`}
                            onClick={() => onToggle(country)}
                        >
                            {country}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CountryFilter;

import React, { useState } from 'react';
import styles from './CountryFilter.module.css';

interface CountryFilterProps {
    countries: string[];
    selectedCountries: string[];
    isLoading: boolean;
    onToggle: (country: string) => void;
}

const CountryFilter: React.FC<CountryFilterProps> = ({
    countries,
    selectedCountries,
    isLoading,
    onToggle
}) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [showAll, setShowAll] = useState(false);

    // Filter countries based on search term
    const filteredCountries = countries.filter(country =>
        country.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Limit displayed countries unless showAll is true
    const displayedCountries = showAll ? filteredCountries : filteredCountries.slice(0, 10);
    const hasMoreCountries = filteredCountries.length > 10;

    return (
        <div className={styles.filterSection}>
            <h3>Kraj produkcji</h3>
            {isLoading ? (
                <div className={styles.loading}>Ładowanie krajów...</div>
            ) : (
                <>
                    {countries.length > 5 && (
                        <div className={styles.searchContainer}>
                            <input
                                type="text"
                                placeholder="Szukaj kraju..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className={styles.searchInput}
                            />
                        </div>
                    )}

                    <div className={styles.countryList}>
                        {displayedCountries.map((country) => (
                            <div
                                key={country}
                                className={`${styles.countryItem} ${selectedCountries.includes(country) ? styles.selected : ''}`}
                                onClick={() => onToggle(country)}
                            >
                                {country}
                            </div>
                        ))}
                    </div>

                    {hasMoreCountries && (
                        <button
                            className={styles.showMoreButton}
                            onClick={() => setShowAll(!showAll)}
                        >
                            {showAll ? 'Pokaż mniej' : 'Pokaż więcej'}
                        </button>
                    )}
                </>
            )}
        </div>
    );
};

export default CountryFilter;

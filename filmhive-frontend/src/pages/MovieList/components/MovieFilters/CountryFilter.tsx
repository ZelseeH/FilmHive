import React, { useState } from 'react';
import styles from './CountryFilter.module.css';

interface CountryFilterProps {
    countries: string[];
    selectedCountries: string[];
    isLoading: boolean;
    onToggle: (country: string) => void;
}

const countryCodeMap: Record<string, string> = {
    AE: 'Zjednoczone Emiraty Arabskie',
    AU: 'Australia',
    BE: 'Belgia',
    BR: 'Brazylia',
    CA: 'Kanada',
    CN: 'Chiny',
    CZ: 'Czechy',
    DE: 'Niemcy',
    DK: 'Dania',
    EG: 'Egipt',
    ES: 'Hiszpania',
    FR: 'Francja',
    GB: 'Wielka Brytania',
    HK: 'Hongkong',
    IE: 'Irlandia',
    IT: 'Włochy',
    JP: 'Japonia',
    KR: 'Korea Południowa',
    MX: 'Meksyk',
    PL: 'Polska',
    US: 'Stany Zjednoczone',
    NZ: 'Nowa Zelandia',
    'Irlandia/UK/USA': 'Irlandia, Wielka Brytania, Stany Zjednoczone',
    UK: 'Wielka Brytania',
    'UK/Australia': 'Wielka Brytania, Australia',
    'UK/USA': 'Wielka Brytania, Stany Zjednoczone',
    USA: 'Stany Zjednoczone',
    'USA/NZ': 'Stany Zjednoczone, Nowa Zelandia',
    'USA/UK': 'Stany Zjednoczone, Wielka Brytania',
};

const CountryFilter: React.FC<CountryFilterProps> = ({
    countries,
    selectedCountries,
    isLoading,
    onToggle,
}) => {
    const [showAll, setShowAll] = useState(false);

    const displayedCountries = showAll ? countries : countries.slice(0, 10);

    return (
        <div className={styles.filterSection}>
            <h3>Kraj produkcji</h3>
            {isLoading ? (
                <div className={styles.loading}>Ładowanie krajów...</div>
            ) : (
                <>
                    <div
                        className={`${styles.countryList} ${showAll ? styles.expanded : ''}`}
                    >
                        {displayedCountries.map((country) => (
                            <div
                                key={country}
                                className={`${styles.countryItem} ${selectedCountries.includes(country) ? styles.selected : ''
                                    }`}
                                onClick={() => onToggle(country)}
                            >
                                {countryCodeMap[country] || country}
                            </div>
                        ))}
                    </div>
                    {countries.length > 10 && (
                        <button
                            className={styles.showMoreButton}
                            onClick={() => setShowAll(!showAll)}
                        >
                            {showAll ? 'Pokaż mniej' : 'Pokaż wszystkie'}
                        </button>
                    )}
                </>
            )}
        </div>
    );
};

export default CountryFilter;

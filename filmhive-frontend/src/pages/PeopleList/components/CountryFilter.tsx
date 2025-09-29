import React, { useState } from 'react';
import styles from './FilterOptions.module.css';

interface CountryFilterProps {
    countries: string[];
    selectedCountries: string[];
    isLoading: boolean;
    onToggle: (country: string) => void;
}

// Mapa tłumaczeń nazw krajów z angielskiego na polski
const countryTranslationsMap: Record<string, string> = {
    Algeria: 'Algieria',
    Argentina: 'Argentyna',
    Australia: 'Australia',
    Austria: 'Austria',
    Belgium: 'Belgia',
    Bermuda: 'Bermudy',
    Brazil: 'Brazylia',
    Bulgaria: 'Bułgaria',
    Canada: 'Kanada',
    'Channel Islands': 'Wyspy Normandzkie',
    Chile: 'Chile',
    China: 'Chiny',
    Chiny: 'Chiny',
    Colombia: 'Kolumbia',
    Cuba: 'Kuba',
    Dania: 'Dania',
    Danmark: 'Dania',
    Denmark: 'Dania',
    England: 'Anglia',
    'Estados Unidos': 'Stany Zjednoczone',
    Florida: 'Floryda',
    France: 'Francja',
    Francja: 'Francja',
    Germany: 'Niemcy',
    Greece: 'Grecja',
    Gwatemala: 'Gwatemala',
    Hiszpania: 'Hiszpania',
    'Hong Kong': 'Hongkong',
    India: 'Indie',
    Indonesia: 'Indonezja',
    Iran: 'Iran',
    Ireland: 'Irlandia',
    Irlandia: 'Irlandia',
    Italia: 'Włochy',
    Italy: 'Włochy',
    Izrael: 'Izrael',
    Japan: 'Japonia',
    Kanada: 'Kanada',
    'Korea Południowa': 'Korea Południowa',
    Lebanon: 'Liban',
    Macau: 'Makau',
    Malaysia: 'Malezja',
    Meksyk: 'Meksyk',
    Mexico: 'Meksyk',
    Nepal: 'Nepal',
    Netherlands: 'Holandia',
    'New Zealand': 'Nowa Zelandia',
    Niemcy: 'Niemcy',
    'Niemcy (obecnie Polska)': 'Niemcy',
    'Nowa Zelandia': 'Nowa Zelandia',
    Oman: 'Oman',
    Panama: 'Panama',
    Philippines: 'Filipiny',
    Poland: 'Polska',
    Polska: 'Polska',
    Portoryko: 'Portoryko',
    'Puerto Rico': 'Portoryko',
    'Romanian SR': 'Rumunia',
    RPA: 'RPA',
    Russia: 'Rosja',
    'Russian Empire': 'Rosja',
    Slovenia: 'Słowenia',
    'South Africa': 'Republika Południowej Afryki',
    'South Korea': 'Korea Południowa',
    Spain: 'Hiszpania',
    Sudan: 'Sudan',
    Swaziland: 'Eswatini',
    Sweden: 'Szwecja',
    Szwecja: 'Szwecja',
    Taiwan: 'Tajwan',
    Tajwan: 'Tajwan',
    Thailand: 'Tajlandia',
    Turkey: 'Turcja',
    Türkiye: 'Turcja',
    'U.S': 'USA',
    'U.S.A.': 'USA',
    UK: 'Wielka Brytania',
    Ukraine: 'Ukraina',
    'United Kingdom': 'Wielka Brytania',
    Uruguay: 'Urugwaj',
    USA: 'USA',
    USSR: 'ZSRR',
    Wales: 'Walia',
    'West Germany': 'Niemcy Zachodnie',
    Wietnam: 'Wietnam',
    Yugoslavia: 'Jugosławia',
    Santiago: 'Santiago',
    Wenecja: 'Wenecja',
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
            <h3>Miejsce urodzenia</h3>
            {isLoading ? (
                <div className={styles.loading}>Ładowanie miejsc...</div>
            ) : (
                <>
                    <div className={styles.filterOptions}>
                        {displayedCountries.map((country) => (
                            <button
                                key={country}
                                className={`${styles.filterOption} ${selectedCountries.includes(country) ? styles.selected : ''
                                    }`}
                                onClick={() => onToggle(country)}
                            >
                                {countryTranslationsMap[country] || country}
                            </button>
                        ))}
                    </div>
                    {countries.length > 10 && (
                        <button
                            className={styles.showAllButton}
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

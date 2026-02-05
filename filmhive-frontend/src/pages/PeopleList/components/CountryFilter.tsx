import React, { useState } from 'react';
import styles from './FilterOptions.module.css';

interface CountryFilterProps {
    countries: string[];
    selectedCountries: string[];
    isLoading: boolean;
    onToggle: (country: string) => void;
}

// Rozszerzona mapa kodów krajów
const countryCodeMap: Record<string, string> = {
    // Podstawowe kody krajów
    AE: 'Zjednoczone Emiraty Arabskie',
    AR: 'Argentyna',
    AT: 'Austria',
    AU: 'Australia',
    BE: 'Belgia',
    BG: 'Bułgaria',
    BR: 'Brazylia',
    BY: 'Białoruś',
    CA: 'Kanada',
    CH: 'Szwajcaria',
    CL: 'Chile',
    CN: 'Chiny',
    CO: 'Kolumbia',
    CU: 'Kuba',
    CZ: 'Czechy',
    DE: 'Niemcy',
    DK: 'Dania',
    DZ: 'Algieria',
    EG: 'Egipt',
    ES: 'Hiszpania',
    FI: 'Finlandia',
    FR: 'Francja',
    GB: 'Wielka Brytania',
    GE: 'Gruzja',
    GR: 'Grecja',
    GT: 'Gwatemala',
    HK: 'Hongkong',
    HR: 'Chorwacja',
    IE: 'Irlandia',
    IL: 'Izrael',
    IN: 'Indie',
    IR: 'Iran',
    IT: 'Włochy',
    JP: 'Japonia',
    KR: 'Korea Południowa',
    KZ: 'Kazachstan',
    LB: 'Liban',
    MA: 'Maroko',
    MX: 'Meksyk',
    MY: 'Malezja',
    NG: 'Nigeria',
    NL: 'Holandia',
    NO: 'Norwegia',
    NP: 'Nepal',
    NZ: 'Nowa Zelandia',
    OM: 'Oman',
    PA: 'Panama',
    PH: 'Filipiny',
    PL: 'Polska',
    PR: 'Portoryko',
    PT: 'Portugalia',
    RO: 'Rumunia',
    RS: 'Serbia',
    RU: 'Rosja',
    SE: 'Szwecja',
    SI: 'Słowenia',
    SZ: 'Eswatini',
    TH: 'Tajlandia',
    TR: 'Turcja',
    TW: 'Tajwan',
    UA: 'Ukraina',
    UK: 'Wielka Brytania',
    US: 'Stany Zjednoczone',
    UY: 'Urugwaj',
    VN: 'Wietnam',
    ZA: 'Republika Południowej Afryki',

    // Angielskie nazwy
    'Algeria': 'Algieria',
    'Argentina': 'Argentyna',
    'Australia': 'Australia',
    'Austria': 'Austria',
    'Belarus': 'Białoruś',
    'Belgium': 'Belgia',
    'Bermuda': 'Bermudy',
    'Brazil': 'Brazylia',
    'Bulgaria': 'Bułgaria',
    'Canada': 'Kanada',
    'Channel Islands': 'Wyspy Normandzkie',
    'Chile': 'Chile',
    'China': 'Chiny',
    'Colombia': 'Kolumbia',
    'Cuba': 'Kuba',
    'Denmark': 'Dania',
    'England': 'Anglia',
    'Finland': 'Finlandia',
    'Florida': 'Stany Zjednoczone',
    'France': 'Francja',
    'Georgia': 'Gruzja',
    'Germany': 'Niemcy',
    'Greece': 'Grecja',
    'Guatemala': 'Gwatemala',
    'Hong Kong': 'Hongkong',
    'India': 'Indie',
    'Indonesia': 'Indonezja',
    'Iran': 'Iran',
    'Ireland': 'Irlandia',
    'Israel': 'Izrael',
    'Italy': 'Włochy',
    'Japan': 'Japonia',
    'Kazakhstan': 'Kazachstan',
    'Lebanon': 'Liban',
    'Macau': 'Makau',
    'Malaysia': 'Malezja',
    'Mexico': 'Meksyk',
    'Nepal': 'Nepal',
    'Netherlands': 'Holandia',
    'New Zealand': 'Nowa Zelandia',
    'Nigeria': 'Nigeria',
    'Norway': 'Norwegia',
    'Oman': 'Oman',
    'Panama': 'Panama',
    'Philippines': 'Filipiny',
    'Poland': 'Polska',
    'Portugal': 'Portugalia',
    'Puerto Rico': 'Portoryko',
    'Romania': 'Rumunia',
    'Russia': 'Rosja',
    'Slovenia': 'Słowenia',
    'South Africa': 'Republika Południowej Afryki',
    'South Korea': 'Korea Południowa',
    'Spain': 'Hiszpania',
    'Sudan': 'Sudan',
    'Sweden': 'Szwecja',
    'Switzerland': 'Szwajcaria',
    'Taiwan': 'Tajwan',
    'Texas': 'Stany Zjednoczone',
    'Thailand': 'Tajlandia',
    'Turkey': 'Turcja',
    'Ukraine': 'Ukraina',
    'United Kingdom': 'Wielka Brytania',
    'Uruguay': 'Urugwaj',
    'USA': 'Stany Zjednoczone',
    'Vietnam': 'Wietnam',
    'Wales': 'Walia',
    'Yugoslavia': 'Jugosławia',

    // Polskie nazwy
    'Algieria': 'Algieria',
    'Argentyna': 'Argentyna',
    'Anglia': 'Anglia',
    'Belgia': 'Belgia',
    'Bermudy': 'Bermudy',
    'Brazylia': 'Brazylia',
    'Bułgaria': 'Bułgaria',
    'Chiny': 'Chiny',
    'Dania': 'Dania',
    'Filipiny': 'Filipiny',
    'Finlandia': 'Finlandia',
    'Francja': 'Francja',
    'Grecja': 'Grecja',
    'Gruzja': 'Gruzja',
    'Gwatemala': 'Gwatemala',
    'Hiszpania': 'Hiszpania',
    'Holandia': 'Holandia',
    'Hongkong': 'Hongkong',
    'Indie': 'Indie',
    'Indonezja': 'Indonezja',
    'Irlandia': 'Irlandia',
    'Izrael': 'Izrael',
    'Japonia': 'Japonia',
    'Jugosławia': 'Jugosławia',
    'Kanada': 'Kanada',
    'Kazachstan': 'Kazachstan',
    'Kolumbia': 'Kolumbia',
    'Korea Południowa': 'Korea Południowa',
    'Kuba': 'Kuba',
    'Liban': 'Liban',
    'Makau': 'Makau',
    'Malezja': 'Malezja',
    'Meksyk': 'Meksyk',
    'Niemcy': 'Niemcy',
    'Norwegia': 'Norwegia',
    'Nowa Zelandia': 'Nowa Zelandia',
    'Polska': 'Polska',
    'Portoryko': 'Portoryko',
    'Portugalia': 'Portugalia',
    'Republika Południowej Afryki': 'Republika Południowej Afryki',
    'Rosja': 'Rosja',
    'Rumunia': 'Rumunia',
    'Słowenia': 'Słowenia',
    'Stany Zjednoczone': 'Stany Zjednoczone',
    'Szwajcaria': 'Szwajcaria',
    'Szwecja': 'Szwecja',
    'Tajlandia': 'Tajlandia',
    'Tajwan': 'Tajwan',
    'Turcja': 'Turcja',
    'Ukraina': 'Ukraina',
    'Urugwaj': 'Urugwaj',
    'Walia': 'Walia',
    'Wielka Brytania': 'Wielka Brytania',
    'Wietnam': 'Wietnam',
    'Włochy': 'Włochy',
    'Wyspy Normandzkie': 'Wyspy Normandzkie',

    // Historyczne nazwy - NORMALIZACJA
    '(obecnie Białoruś': 'Białoruś',
    'Austro-Węgry (obecnie Polska': 'Austria',
    'Dahomey [now Benin': 'Benin',
    'French Protectorate in Morocco [now Morocco': 'Maroko',
    'German Democratic Republic [now Germany': 'Niemcy',
    'Niemcy (obecnie Polska': 'Polska',
    'Polska (obecnie Ukraina': 'Ukraina',
    'Polska [obecnie Ukraina': 'Ukraina',
    'Romanian SR [now Romania': 'Rumunia',
    'Rzesza Niemiecka (obecnie Polska': 'Polska',
    'Swaziland [now Eswatini': 'Eswatini',
    'USSR [now Russia': 'Rosja',
    'USSR [now Ukraine': 'Ukraina',
    'West Germany [now Germany': 'Niemcy',
    'Niemcy Zachodnie': 'Niemcy',
    'Yugoslavia [now Croatia': 'Chorwacja',
    'Yugoslavia [now Serbia': 'Serbia',
    'ZSRR (obecnie Ukraina': 'Ukraina',

    // Stany USA
    'Michigan. USA': 'Stany Zjednoczone',
    'Michigan': 'Stany Zjednoczone',
    'Ohio': 'Stany Zjednoczone',
    'Floryda, Stany Zjednoczone': 'Stany Zjednoczone',
    'Teksas, Stany Zjednoczone': 'Stany Zjednoczone',

    // Miasta
    'Santiago - Chile': 'Chile',
    'Wenecja': 'Włochy',
    'Czerwińsk': 'Polska',
    'Działoszyce': 'Polska',

    // Inne formy
    'RPA': 'Republika Południowej Afryki',
    'США': 'Stany Zjednoczone',
    'Benin': 'Benin',
    'Maroko': 'Maroko',
    'Eswatini': 'Eswatini',
    'Chorwacja': 'Chorwacja',
    'Serbia': 'Serbia',
};

const normalizeCountryName = (location: string): string => {
    if (!location) return '';

    // Usuń spacje i nawiasy na końcu
    let trimmed = location.trim().replace(/\s+/g, ' ');
    trimmed = trimmed.replace(/[\[\]()]+$/g, '').trim();

    // Dokładne dopasowanie
    if (countryCodeMap[trimmed]) {
        return countryCodeMap[trimmed];
    }

    // Sprawdź czy zaczyna się od "(" - usuń nawias otwierający
    if (trimmed.startsWith('(')) {
        trimmed = trimmed.substring(1);
        if (countryCodeMap[trimmed]) {
            return countryCodeMap[trimmed];
        }
    }

    // Sprawdź bez ostatniego znaku (usuń niepełne nawiasy)
    const withoutLast = trimmed.slice(0, -1);
    if (countryCodeMap[withoutLast]) {
        return countryCodeMap[withoutLast];
    }

    // Format "Miasto, Kraj"
    if (trimmed.includes(',')) {
        const parts = trimmed.split(',').map(p => p.trim());
        const country = parts[parts.length - 1];
        if (countryCodeMap[country]) {
            return countryCodeMap[country];
        }
    }

    // Format "Miasto - Kraj"
    if (trimmed.includes(' - ')) {
        const parts = trimmed.split(' - ').map(p => p.trim());
        const country = parts[parts.length - 1];
        if (countryCodeMap[country]) {
            return countryCodeMap[country];
        }
    }

    // Case-insensitive
    const lowerTrimmed = trimmed.toLowerCase();
    const matchingKey = Object.keys(countryCodeMap).find(
        key => key.toLowerCase() === lowerTrimmed
    );
    if (matchingKey) {
        return countryCodeMap[matchingKey];
    }

    return trimmed;
};

const CountryFilter: React.FC<CountryFilterProps> = ({
    countries,
    selectedCountries,
    isLoading,
    onToggle,
}) => {
    const [showAll, setShowAll] = useState(false);

    // Normalizuj i pogrupuj
    const countryGroups = countries.reduce((acc, country) => {
        const normalized = normalizeCountryName(country);
        if (!acc[normalized]) {
            acc[normalized] = [];
        }
        acc[normalized].push(country);
        return acc;
    }, {} as Record<string, string[]>);

    // Utwórz listę unikalnych krajów z licznikami
    const uniqueCountries = Object.entries(countryGroups).map(([normalized, originals]) => ({
        normalized,
        originals,
        count: originals.length,
        // Pierwszy oryginalny dla onToggle
        firstOriginal: originals[0]
    })).sort((a, b) => a.normalized.localeCompare(b.normalized, 'pl'));

    const displayedCountries = showAll
        ? uniqueCountries
        : uniqueCountries.slice(0, 10);

    return (
        <div className={styles.filterSection}>
            <h3>Miejsce urodzenia</h3>
            {isLoading ? (
                <div className={styles.loading}>Ładowanie miejsc...</div>
            ) : (
                <>
                    <div className={styles.filterOptions}>
                        {displayedCountries.map(({ normalized, originals, count, firstOriginal }) => {
                            const isSelected = originals.some(orig => selectedCountries.includes(orig));

                            return (
                                <button
                                    key={firstOriginal}
                                    className={`${styles.filterOption} ${isSelected ? styles.selected : ''
                                        }`}
                                    onClick={() => {
                                        // Toggle wszystkie oryginalne wartości
                                        originals.forEach(orig => onToggle(orig));
                                    }}
                                    title={count > 1 ? `${count} wariantów: ${originals.join(', ')}` : undefined}
                                >
                                    {normalized}
                                </button>
                            );
                        })}
                    </div>
                    {countries.length > 10 && (
                        <button
                            className={styles.showAllButton}
                            onClick={() => setShowAll(!showAll)}
                        >
                            {showAll ? 'Pokaż mniej' : `Pokaż więcej (${uniqueCountries.length})`}
                        </button>
                    )}
                </>
            )}
        </div>
    );
};

export default CountryFilter;

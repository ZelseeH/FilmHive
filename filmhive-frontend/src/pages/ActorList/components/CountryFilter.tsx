import React, { useState } from 'react';
import styles from './FilterOptions.module.css';

interface CountryFilterProps {
    countries: string[];
    selectedCountries: string[];
    isLoading: boolean;
    onToggle: (country: string) => void;
}

// Rozszerzona mapa kodów krajów, miast i historycznych nazw
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
    CR: 'Kostaryka',
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
    PE: 'Peru',
    PH: 'Filipiny',
    PL: 'Polska',
    PR: 'Portoryko',
    PT: 'Portugalia',
    RO: 'Rumunia',
    RS: 'Serbia',
    RU: 'Rosja',
    SE: 'Szwecja',
    SI: 'Słowenia',
    SU: 'ZSRR',
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

    // Angielskie nazwy krajów
    'Algeria': 'Algieria',
    'Argentina': 'Argentyna',
    'Australia': 'Australia',
    'Austria': 'Austria',
    'Belarus': 'Białoruś',
    'Belgium': 'Belgia',
    'Bermuda': 'Bermudy',
    'Bermudy': 'Bermudy',
    'Brazil': 'Brazylia',
    'Bulgaria': 'Bułgaria',
    'Bułgaria': 'Bułgaria',
    'Canada': 'Kanada',
    'Kanada': 'Kanada',
    'Channel Islands': 'Wyspy Normandzkie',
    'Wyspy Normandzkie': 'Wyspy Normandzkie',
    'Chile': 'Chile',
    'China': 'Chiny',
    'Chiny': 'Chiny',
    'Colombia': 'Kolumbia',
    'Cuba': 'Kuba',
    'Kuba': 'Kuba',
    'Denmark': 'Dania',
    'Dania': 'Dania',
    'England': 'Anglia',
    'Anglia': 'Anglia',
    'Finland': 'Finlandia',
    'Finlandia': 'Finlandia',
    'Florida': 'Floryda, Stany Zjednoczone',
    'France': 'Francja',
    'Francja': 'Francja',
    'Georgia': 'Gruzja',
    'Germany': 'Niemcy',
    'Niemcy': 'Niemcy',
    'Greece': 'Grecja',
    'Grecja': 'Grecja',
    'Guatemala': 'Gwatemala',
    'Gwatemala': 'Gwatemala',
    'Hong Kong': 'Hongkong',
    'Hongkong': 'Hongkong',
    'India': 'Indie',
    'Indie': 'Indie',
    'Indonesia': 'Indonezja',
    'Indonezja': 'Indonezja',
    'Iran': 'Iran',
    'Ireland': 'Irlandia',
    'Irlandia': 'Irlandia',
    'Israel': 'Izrael',
    'Izrael': 'Izrael',
    'Italy': 'Włochy',
    'Włochy': 'Włochy',
    'Japan': 'Japonia',
    'Japonia': 'Japonia',
    'Kazakhstan': 'Kazachstan',
    'Kazachstan': 'Kazachstan',
    'Lebanon': 'Liban',
    'Liban': 'Liban',
    'Macau': 'Makau',
    'Makau': 'Makau',
    'Malaysia': 'Malezja',
    'Malezja': 'Malezja',
    'Mexico': 'Meksyk',
    'Meksyk': 'Meksyk',
    'Nepal': 'Nepal',
    'Netherlands': 'Holandia',
    'Holandia': 'Holandia',
    'New Zealand': 'Nowa Zelandia',
    'Nowa Zelandia': 'Nowa Zelandia',
    'Nigeria': 'Nigeria',
    'Norway': 'Norwegia',
    'Norwegia': 'Norwegia',
    'Oman': 'Oman',
    'Panama': 'Panama',
    'Philippines': 'Filipiny',
    'Filipiny': 'Filipiny',
    'Poland': 'Polska',
    'Polska': 'Polska',
    'Portugal': 'Portugalia',
    'Portugalia': 'Portugalia',
    'Puerto Rico': 'Portoryko',
    'Portoryko': 'Portoryko',
    'Romania': 'Rumunia',
    'Rumunia': 'Rumunia',
    'Russia': 'Rosja',
    'Rosja': 'Rosja',
    'Slovenia': 'Słowenia',
    'Słowenia': 'Słowenia',
    'South Africa': 'Republika Południowej Afryki',
    'Republika Południowej Afryki': 'Republika Południowej Afryki',
    'South Korea': 'Korea Południowa',
    'Korea Południowa': 'Korea Południowa',
    'Spain': 'Hiszpania',
    'Hiszpania': 'Hiszpania',
    'Sudan': 'Sudan',
    'Sweden': 'Szwecja',
    'Szwecja': 'Szwecja',
    'Switzerland': 'Szwajcaria',
    'Szwajcaria': 'Szwajcaria',
    'Taiwan': 'Tajwan',
    'Tajwan': 'Tajwan',
    'Texas': 'Teksas, Stany Zjednoczone',
    'Thailand': 'Tajlandia',
    'Tajlandia': 'Tajlandia',
    'Turkey': 'Turcja',
    'Turcja': 'Turcja',
    'Ukraine': 'Ukraina',
    'Ukraina': 'Ukraina',
    'United Kingdom': 'Wielka Brytania',
    'Wielka Brytania': 'Wielka Brytania',
    'Uruguay': 'Urugwaj',
    'Urugwaj': 'Urugwaj',
    'USA': 'Stany Zjednoczone',
    'U.S.': 'Stany Zjednoczone',
    'U.S.A': 'Stany Zjednoczone',
    'Vietnam': 'Wietnam',
    'Wietnam': 'Wietnam',
    'Wales': 'Walia',
    'Walia': 'Walia',
    'Yugoslavia': 'Jugosławia',
    'Jugosławia': 'Jugosławia',

    // Francuskie nazwy
    'Algérie': 'Algieria',
    'Méxicó': 'Meksyk',

    // Historyczne nazwy z "obecnie"
    '(obecnie Białoruś)': 'Białoruś',
    'Austro-Węgry (obecnie Polska)': 'Polska',
    'German Democratic Republic [now Germany]': 'Niemcy',
    'Dahomey [now Benin]': 'Benin',
    'French Protectorate in Morocco [now Morocco]': 'Maroko',
    'Swaziland [now Eswatini]': 'Eswatini',
    'West Germany [now Germany]': 'Niemcy',
    'Yugoslavia [now Croatia]': 'Chorwacja',
    'Yugoslavia [now Serbia]': 'Serbia',
    'USSR [now Russia]': 'Rosja',
    'USSR [now Ukraine]': 'Ukraina',
    'ZSRR (obecnie Ukraina)': 'Ukraina',
    'Polska (obecnie Ukraina)': 'Ukraina',
    'Polska [obecnie Ukraina]': 'Ukraina',
    'Rzesza Niemiecka (obecnie Polska)': 'Polska',
    'Romanian SR [now Romania]': 'Rumunia',
    'Mexico]': 'Meksyk',
    'Poland]': 'Polska',
    'Russia)': 'Rosja',
    'Russia]': 'Rosja',
    'Ukraine]': 'Ukraina',

    // Stany USA
    'Michigan. USA': 'Michigan, Stany Zjednoczone',
    'Michigan': 'Michigan, Stany Zjednoczone',
    'Ohio': 'Ohio, Stany Zjednoczone',
    'OH': 'Ohio, Stany Zjednoczone',

    // Miasta
    'Santiago - Chile': 'Chile',
    'Wenecja': 'Włochy',
    'Venice': 'Włochy',
    'Warszawa': 'Polska',
    'Warsaw': 'Polska',
    'Kraków': 'Polska',
    'Łódź': 'Polska',
    'Czerwińsk': 'Polska',
    'Działoszyce': 'Polska',

    // Kombinacje krajów
    'Irlandia/UK/USA': 'Irlandia, Wielka Brytania, Stany Zjednoczone',
    'UK/Australia': 'Wielka Brytania, Australia',
    'UK/USA': 'Wielka Brytania, Stany Zjednoczone',
    'USA/NZ': 'Stany Zjednoczone, Nowa Zelandia',
    'USA/UK': 'Stany Zjednoczone, Wielka Brytania',

    // Duplikaty i błędne zapisy
    'США': 'Stany Zjednoczone', // Cyrylica
    'RPR': 'Republika Południowej Afryki',
    'RPA': 'Republika Południowej Afryki',
    'Benin': 'Benin',
    'Maroko': 'Maroko',
    'Eswatini': 'Eswatini',
    'Chorwacja': 'Chorwacja',
    'Serbia': 'Serbia',
};

// Funkcja do normalizacji nazwy kraju/miasta
const normalizeCountryName = (location: string): string => {
    if (!location) return '';

    // Usuń nadmiarowe spacje i przecinki
    let trimmed = location.trim().replace(/\s+/g, ' ');

    // Usuń nawiasy kwadratowe i okrągłe na końcu (np. "Poland]" → "Poland")
    trimmed = trimmed.replace(/[\[\]()]+$/g, '');

    // Sprawdź czy jest w mapie (dokładne dopasowanie)
    if (countryCodeMap[trimmed]) {
        return countryCodeMap[trimmed];
    }

    // Sprawdź czy zawiera "now" (np. "USSR [now Ukraine]")
    if (trimmed.includes('[now') || trimmed.includes('(obecnie')) {
        const match = trimmed.match(/\[now ([^\]]+)\]/) || trimmed.match(/\(obecnie ([^)]+)\)/);
        if (match && match[1]) {
            const modernCountry = match[1].trim();
            return countryCodeMap[modernCountry] || modernCountry;
        }
    }

    // Jeśli format "Miasto, Kraj" → weź tylko kraj
    if (trimmed.includes(',')) {
        const parts = trimmed.split(',').map(p => p.trim());
        const country = parts[parts.length - 1]; // Ostatnia część to kraj

        // Sprawdź czy kraj jest w mapie
        if (countryCodeMap[country]) {
            return countryCodeMap[country];
        }

        // Jeśli miasto polskie (sprawdź pierwszą część)
        const city = parts[0];
        if (city && /^[A-ZĄĆĘŁŃÓŚŹŻ]/.test(city)) {
            return 'Polska';
        }
    }

    // Jeśli zawiera "-" (np. "Santiago - Chile")
    if (trimmed.includes(' - ')) {
        const parts = trimmed.split(' - ').map(p => p.trim());
        const country = parts[parts.length - 1];
        if (countryCodeMap[country]) {
            return countryCodeMap[country];
        }
    }

    // Case-insensitive search w mapie
    const lowerTrimmed = trimmed.toLowerCase();
    const matchingKey = Object.keys(countryCodeMap).find(
        key => key.toLowerCase() === lowerTrimmed
    );
    if (matchingKey) {
        return countryCodeMap[matchingKey];
    }

    // Zwróć oryginał jeśli nie znaleziono
    return trimmed;
};

const CountryFilter: React.FC<CountryFilterProps> = ({
    countries,
    selectedCountries,
    isLoading,
    onToggle
}) => {
    const [showAll, setShowAll] = useState(false);

    // Normalizuj i pogrupuj kraje
    const normalizedCountries = countries.map(country => ({
        original: country,
        normalized: normalizeCountryName(country)
    }));

    // Usuń duplikaty (te same znormalizowane kraje)
    const uniqueCountries = normalizedCountries.reduce((acc, { original, normalized }) => {
        const existing = acc.find(item => item.normalized === normalized);
        if (!existing) {
            acc.push({ original, normalized, count: 1, originals: [original] });
        } else {
            existing.count++;
            existing.originals.push(original);
        }
        return acc;
    }, [] as { original: string; normalized: string; count: number; originals: string[] }[]);

    // Sortuj alfabetycznie po polsku
    const sortedCountries = uniqueCountries.sort((a, b) =>
        a.normalized.localeCompare(b.normalized, 'pl')
    );

    const displayedCountries = showAll
        ? sortedCountries
        : sortedCountries.slice(0, 10);

    return (
        <div className={styles.filterSection}>
            <h3>Miejsce urodzenia</h3>
            {isLoading ? (
                <div className={styles.loading}>Ładowanie miejsc...</div>
            ) : (
                <>
                    <div className={`${styles.filterOptions} ${showAll ? styles.expanded : ''}`}>
                        {displayedCountries.map(({ original, normalized, count, originals }) => {
                            const isSelected = originals.some(orig => selectedCountries.includes(orig));

                            return (
                                <button
                                    key={original}
                                    className={`${styles.filterOption} ${isSelected ? styles.selected : ''
                                        }`}
                                    onClick={() => onToggle(original)}
                                    title={count > 1 ? `${count} miejsc: ${originals.join(', ')}` : undefined}
                                >
                                    {normalized}
                                    {count > 1 && <span className={styles.countBadge}>{count}</span>}
                                </button>
                            );
                        })}
                    </div>
                    {countries.length > 10 && (
                        <button
                            className={styles.showMoreButton}
                            onClick={() => setShowAll(!showAll)}
                        >
                            {showAll ? 'Pokaż mniej' : `Pokaż wszystkie (${sortedCountries.length})`}
                        </button>
                    )}
                </>
            )}
        </div>
    );
};

export default CountryFilter;

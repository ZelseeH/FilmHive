import React, { useState } from 'react';
import styles from './CountryFilter.module.css';

interface CountryFilterProps {
    countries: string[];
    selectedCountries: string[];
    isLoading: boolean;
    onToggle: (country: string) => void;
}

const countryCodeMap: Record<string, string> = {
    // Kody krajów
    AE: 'Zjednoczone Emiraty Arabskie',
    AR: 'Argentyna',
    AT: 'Austria',
    AU: 'Australia',
    BE: 'Belgia',
    BR: 'Brazylia',
    BG: 'Bułgaria',
    CA: 'Kanada',
    CH: 'Szwajcaria',
    CL: 'Chile',
    CN: 'Chiny',
    CO: 'Kolumbia',
    CG: 'Kongo',
    CZ: 'Czechy',
    DE: 'Niemcy',
    DK: 'Dania',
    DZ: 'Algieria',
    EG: 'Egipt',
    ES: 'Hiszpania',
    EE: 'Estonia',
    FI: 'Finlandia',
    FR: 'Francja',
    GB: 'Wielka Brytania',
    GR: 'Grecja',
    HK: 'Hongkong',
    HU: 'Węgry',
    IE: 'Irlandia',
    IS: 'Islandia',
    IL: 'Izrael',
    IN: 'Indie',
    ID: 'Indonezja',
    IT: 'Włochy',
    JP: 'Japonia',
    KR: 'Korea Południowa',
    LV: 'Łotwa',
    LU: 'Luksemburg',
    MX: 'Meksyk',
    NL: 'Holandia',
    NZ: 'Nowa Zelandia',
    NO: 'Norwegia',
    PH: 'Filipiny',
    PL: 'Polska',
    RO: 'Rumunia',
    RU: 'Rosja',
    RS: 'Serbia',
    ZA: 'Republika Południowej Afryki',
    SE: 'Szwecja',
    TW: 'Tajwan',
    TH: 'Tajlandia',
    TR: 'Turcja',
    UA: 'Ukraina',
    UK: 'Wielka Brytania',
    US: 'Stany Zjednoczone',

    // Angielskie nazwy krajów
    'Algeria': 'Algieria',
    'Argentina': 'Argentyna',
    'Australia': 'Australia',
    'Austria': 'Austria',
    'Belgium': 'Belgia',
    'Brazil': 'Brazylia',
    'Bulgaria': 'Bułgaria',
    'Canada': 'Kanada',
    'Chile': 'Chile',
    'China': 'Chiny',
    'Colombia': 'Kolumbia',
    'Congo': 'Kongo',
    'Czech Republic': 'Czechy',
    'Denmark': 'Dania',
    'Egypt': 'Egipt',
    'Estonia': 'Estonia',
    'Finland': 'Finlandia',
    'France': 'Francja',
    'Germany': 'Niemcy',
    'Greece': 'Grecja',
    'Hong Kong': 'Hongkong',
    'Hungary': 'Węgry',
    'Iceland': 'Islandia',
    'India': 'Indie',
    'Indonesia': 'Indonezja',
    'Ireland': 'Irlandia',
    'Israel': 'Izrael',
    'Italy': 'Włochy',
    'Japan': 'Japonia',
    'Latvia': 'Łotwa',
    'Luxembourg': 'Luksemburg',
    'Mexico': 'Meksyk',
    'Netherlands': 'Holandia',
    'New Zealand': 'Nowa Zelandia',
    'Norway': 'Norwegia',
    'Philippines': 'Filipiny',
    'Poland': 'Polska',
    'Romania': 'Rumunia',
    'Russia': 'Rosja',
    'Serbia': 'Serbia',
    'South Africa': 'Republika Południowej Afryki',
    'South Korea': 'Korea Południowa',
    'Spain': 'Hiszpania',
    'Sweden': 'Szwecja',
    'Switzerland': 'Szwajcaria',
    'Taiwan': 'Tajwan',
    'Thailand': 'Tajlandia',
    'Turkey': 'Turcja',
    'Ukraine': 'Ukraina',
    'United Arab Emirates': 'Zjednoczone Emiraty Arabskie',
    'United Kingdom': 'Wielka Brytania',
    'United States of America': 'Stany Zjednoczone',
    'USA': 'Stany Zjednoczone',

    // Polskie nazwy
    'Algieria': 'Algieria',
    'Argentyna': 'Argentyna',
    'Belgia': 'Belgia',
    'Brazylia': 'Brazylia',
    'Bułgaria': 'Bułgaria',
    'Czechy': 'Czechy',
    'Dania': 'Dania',
    'Egipt': 'Egipt',
    'Finlandia': 'Finlandia',
    'Francja': 'Francja',
    'Hiszpania': 'Hiszpania',
    'Holandia': 'Holandia',
    'Hongkong': 'Hongkong',
    'Indie': 'Indie',
    'Indonezja': 'Indonezja',
    'Irlandia': 'Irlandia',
    'Islandia': 'Islandia',
    'Izrael': 'Izrael',
    'Japonia': 'Japonia',
    'Kanada': 'Kanada',
    'Kolumbia': 'Kolumbia',
    'Kongo': 'Kongo',
    'Korea Południowa': 'Korea Południowa',
    'Łotwa': 'Łotwa',
    'Luksemburg': 'Luksemburg',
    'Meksyk': 'Meksyk',
    'Niemcy': 'Niemcy',
    'Norwegia': 'Norwegia',
    'Nowa Zelandia': 'Nowa Zelandia',
    'Polska': 'Polska',
    'Republika Południowej Afryki': 'Republika Południowej Afryki',
    'Rosja': 'Rosja',
    'Rumunia': 'Rumunia',
    'Stany Zjednoczone': 'Stany Zjednoczone',
    'Szwajcaria': 'Szwajcaria',
    'Szwecja': 'Szwecja',
    'Tajlandia': 'Tajlandia',
    'Tajwan': 'Tajwan',
    'Turcja': 'Turcja',
    'Ukraina': 'Ukraina',
    'Węgry': 'Węgry',
    'Wielka Brytania': 'Wielka Brytania',
    'Włochy': 'Włochy',
    'Zjednoczone Emiraty Arabskie': 'Zjednoczone Emiraty Arabskie',

    // Stare formaty ze slashem
    'Irlandia/UK/USA': 'Irlandia',
    'UK/Australia': 'Wielka Brytania',
    'UK/USA': 'Wielka Brytania',
    'USA/NZ': 'Stany Zjednoczone',
    'USA/UK': 'Stany Zjednoczone',
};

// Funkcja do rozdzielania kombinacji krajów
const splitCountries = (country: string): string[] => {
    // Jeśli zawiera przecinek - podziel
    if (country.includes(',')) {
        return country.split(',').map(c => c.trim());
    }
    // Jeśli zawiera slash - podziel
    if (country.includes('/')) {
        return country.split('/').map(c => c.trim());
    }
    return [country];
};

const normalizeCountryName = (country: string): string => {
    if (!country) return '';

    const trimmed = country.trim();

    // Dokładne dopasowanie
    if (countryCodeMap[trimmed]) {
        return countryCodeMap[trimmed];
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

    // Rozdziel kombinacje krajów i normalizuj
    const expandedCountries = countries.flatMap(country => {
        const parts = splitCountries(country);
        return parts.map(part => ({
            original: country, // Oryginalny string z bazy
            part: part,        // Pojedynczy kraj
            normalized: normalizeCountryName(part)
        }));
    });

    // Pogrupuj według znormalizowanej nazwy
    const countryGroups = expandedCountries.reduce((acc, { original, part, normalized }) => {
        if (!acc[normalized]) {
            acc[normalized] = [];
        }
        // Dodaj tylko jeśli jeszcze nie ma tego oryginału
        if (!acc[normalized].some(item => item.original === original)) {
            acc[normalized].push({ original, part });
        }
        return acc;
    }, {} as Record<string, { original: string; part: string }[]>);

    // Unikalne kraje, posortowane alfabetycznie
    const uniqueCountries = Object.entries(countryGroups)
        .map(([normalized, items]) => ({
            normalized,
            originals: items.map(i => i.original),
            firstOriginal: items[0].original
        }))
        .sort((a, b) => a.normalized.localeCompare(b.normalized, 'pl'));

    const displayedCountries = showAll
        ? uniqueCountries
        : uniqueCountries.slice(0, 10);

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
                        {displayedCountries.map(({ normalized, originals, firstOriginal }) => {
                            const isSelected = originals.some(orig => selectedCountries.includes(orig));

                            return (
                                <div
                                    key={firstOriginal}
                                    className={`${styles.countryItem} ${isSelected ? styles.selected : ''
                                        }`}
                                    onClick={() => {
                                        // Toggle wszystkie warianty
                                        originals.forEach(orig => onToggle(orig));
                                    }}
                                >
                                    {normalized}
                                </div>
                            );
                        })}
                    </div>
                    {countries.length > 10 && (
                        <button
                            className={styles.showMoreButton}
                            onClick={() => setShowAll(!showAll)}
                        >
                            {showAll ? 'Pokaż mniej' : `Pokaż wszystkie (${uniqueCountries.length})`}
                        </button>
                    )}
                </>
            )}
        </div>
    );
};

export default CountryFilter;

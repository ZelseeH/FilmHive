import React, { useState, useEffect } from 'react';
import styles from './MovieFilter.module.css';
import { useGenres } from '../../hooks/useGenres';
import { useCountries } from '../../hooks/useCountries';
import { useYearsRange } from '../../hooks/useYearsRange';
import SearchInput from './SearchInput';
import CountryFilter from './CountryFilter';
import YearFilter from './YearFilter';
import GenreFilter from './GenreFilter';
import RatingCountSlider from './RatingCountSlider';
import AverageRatingFilter from './AverageRatingFilter';
import { IoMdClose } from 'react-icons/io';
import { useSearchParams } from 'react-router-dom';

interface MovieFilters {
    title?: string;
    countries?: string;
    years?: string;
    genres?: string;
    rating_count_min?: number;
    average_rating?: number;
}

interface MovieFilterProps {
    value: MovieFilters;
    onChange: (filters: MovieFilters) => void;
    onClose?: () => void;
    isLoading?: boolean;
}

const MovieFilter: React.FC<MovieFilterProps> = ({ value, onChange, onClose, isLoading }) => {
    // Lokalne stany dla filtrów
    const [inputValue, setInputValue] = useState<string>(value.title || '');
    const [selectedCountries, setSelectedCountries] = useState<string[]>(
        value.countries ? value.countries.split(',') : []
    );
    const [selectedYears, setSelectedYears] = useState<string[]>(
        value.years ? value.years.split(',') : []
    );
    const [selectedGenres, setSelectedGenres] = useState<string[]>(
        value.genres ? value.genres.split(',') : []
    );
    const [ratingCountMin, setRatingCountMin] = useState<number>(value.rating_count_min || 0);
    const [averageRating, setAverageRating] = useState<number>(value.average_rating || 0);

    // Aktualizuj stany, gdy zmienią się wartości props
    useEffect(() => {
        setInputValue(value.title || '');
        setSelectedCountries(value.countries ? value.countries.split(',') : []);
        setSelectedYears(value.years ? value.years.split(',') : []);
        setSelectedGenres(value.genres ? value.genres.split(',') : []);
        setRatingCountMin(value.rating_count_min || 0);
        setAverageRating(value.average_rating || 0);
    }, [value]);

    const { genres, isLoadingGenres } = useGenres();
    const { countries, isLoadingCountries } = useCountries();
    const {
        showAllYears,
        displayedYears,
        handleShowAllYears,
        handleShowLessYears
    } = useYearsRange();

    // Funkcje obsługujące zmiany w filtrach
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value);
    };

    const handleClear = () => {
        setInputValue('');
    };

    const toggleCountry = (country: string) => {
        setSelectedCountries(prev =>
            prev.includes(country)
                ? prev.filter(c => c !== country)
                : [...prev, country]
        );
    };

    const toggleYears = (year: string) => {
        setSelectedYears(prev => {
            const isSelected = prev.includes(year);
            return isSelected
                ? prev.filter(y => y !== year)
                : [...prev, year];
        });
    };

    const toggleGenre = (genre: string) => {
        setSelectedGenres(prev =>
            prev.includes(genre)
                ? prev.filter(g => g !== genre)
                : [...prev, genre]
        );
    };

    const setYearsDirectly = (years: string[]) => {
        setSelectedYears(years);
    };

    const handleRatingCountMinChange = (value: number) => {
        setRatingCountMin(value);
    };

    const handleAverageRatingChange = (value: number) => {
        setAverageRating(value);
    };

    const prepareFilters = (): MovieFilters => {
        const filters: MovieFilters = {};
        if (inputValue) filters.title = inputValue;
        if (selectedCountries.length > 0) filters.countries = selectedCountries.join(',');
        if (selectedYears.length > 0) filters.years = selectedYears.join(',');
        if (selectedGenres.length > 0) filters.genres = selectedGenres.join(',');
        if (ratingCountMin > 0) filters.rating_count_min = ratingCountMin;
        if (averageRating > 0) filters.average_rating = averageRating;
        return filters;
    };

    const handleSearch = () => {
        const newFilters = prepareFilters();
        console.log("Applying filters:", newFilters);
        onChange(newFilters);
        if (onClose) onClose();
    };

    const handleClearFilters = () => {
        // Wyczyść wszystkie lokalne stany
        setInputValue('');
        setSelectedCountries([]);
        setSelectedYears([]);
        setSelectedGenres([]);
        setRatingCountMin(0);
        setAverageRating(0);

        // Wyślij puste filtry do rodzica
        onChange({});
    };

    return (
        <div className={styles.filterForm}>
            <div className={styles.filterContent}>
                <SearchInput
                    value={inputValue}
                    onChange={handleInputChange}
                    onClear={handleClear}
                    onSubmit={(e) => {
                        e.preventDefault();
                        handleSearch();
                    }}
                    placeholder="Szukaj filmów..."
                />

                <RatingCountSlider
                    value={ratingCountMin}
                    onChange={handleRatingCountMinChange}
                />

                <AverageRatingFilter
                    value={averageRating}
                    onChange={handleAverageRatingChange}
                />

                <GenreFilter
                    genres={genres}
                    selectedGenres={selectedGenres}
                    isLoading={isLoadingGenres}
                    onToggle={toggleGenre}
                />

                <CountryFilter
                    countries={countries}
                    selectedCountries={selectedCountries}
                    isLoading={isLoadingCountries}
                    onToggle={toggleCountry}
                />

                <YearFilter
                    years={displayedYears}
                    selectedYears={selectedYears}
                    showAllYears={showAllYears}
                    onToggle={toggleYears}
                    onForceSelect={setYearsDirectly}
                    onShowAll={handleShowAllYears}
                    onShowLess={handleShowLessYears}
                />
            </div>

            <div className={styles.filterActions}>
                <button
                    className={styles.clearFiltersButton}
                    onClick={handleClearFilters}
                    type="button"
                >
                    Wyczyść filtry
                </button>

                <button
                    className={styles.searchButton}
                    onClick={handleSearch}
                    type="button"
                >
                    Szukaj
                </button>
            </div>

            {onClose && (
                <div className={styles.closeButtonContainer}>
                    <button
                        onClick={onClose}
                        className={styles.closeFilterButtonLarge}
                        type="button"
                    >
                        <IoMdClose size={24} />
                    </button>
                </div>
            )}
        </div>
    );
};

export default MovieFilter;

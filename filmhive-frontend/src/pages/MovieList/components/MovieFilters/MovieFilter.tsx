import React, { useState } from 'react';
import styles from './MovieFilter.module.css';
import { useMovieFilters } from '../../hooks/useMovieFilters';
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
    const [localFilters, setLocalFilters] = useState<MovieFilters>(value);

    const {
        inputValue,
        selectedCountries,
        selectedYears,
        selectedGenres,
        ratingCountMin,
        averageRating,
        handleInputChange,
        handleClear,
        toggleCountry,
        toggleYears,
        toggleGenre,
        setYearsDirectly,
        handleRatingCountMinChange,
        handleAverageRatingChange,
        setFiltersDirectly
    } = useMovieFilters(value, setLocalFilters);

    const { genres, isLoadingGenres } = useGenres();
    const { countries, isLoadingCountries } = useCountries();
    const {
        showAllYears,
        displayedYears,
        handleShowAllYears,
        handleShowLessYears
    } = useYearsRange();

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
        setFiltersDirectly({});
        // Nie wywołujemy onChange, aby nie przeładowywać strony
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
                >
                    Wyczyść filtry
                </button>

                <button
                    className={styles.searchButton}
                    onClick={handleSearch}
                >
                    Szukaj
                </button>
            </div>

            {onClose && (
                <div className={styles.closeButtonContainer}>
                    <button onClick={onClose} className={styles.closeFilterButtonLarge}>
                        <IoMdClose size={24} />
                    </button>
                </div>
            )}
        </div>
    );
};

export default MovieFilter;

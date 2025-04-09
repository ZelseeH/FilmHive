import { useState, useEffect } from 'react';

interface MovieFilters {
    title?: string;
    countries?: string;
    years?: string;
    genres?: string;
    rating_count_min?: number;
    average_rating?: number;
}

export const useMovieFilters = (initialValue: MovieFilters, onChange: (filters: MovieFilters) => void) => {
    const [inputValue, setInputValue] = useState<string>(initialValue.title || '');
    const [selectedCountries, setSelectedCountries] = useState<string[]>(
        initialValue.countries ? initialValue.countries.split(',') : []
    );
    const [selectedYears, setSelectedYears] = useState<string[]>(
        initialValue.years ? initialValue.years.split(',') : []
    );
    const [selectedGenres, setSelectedGenres] = useState<string[]>(
        initialValue.genres ? initialValue.genres.split(',') : []
    );
    const [ratingCountMin, setRatingCountMin] = useState<number>(initialValue.rating_count_min || 0);
    const [averageRating, setAverageRating] = useState<number>(initialValue.average_rating || 0);
    const setYearsDirectly = (years: string[]) => {
        setSelectedYears(years);
    };


    // Update states when initialValue changes
    useEffect(() => {
        setInputValue(initialValue.title || '');
        setSelectedCountries(initialValue.countries ? initialValue.countries.split(',') : []);
        setSelectedYears(initialValue.years ? initialValue.years.split(',') : []);
        setSelectedGenres(initialValue.genres ? initialValue.genres.split(',') : []);
        setRatingCountMin(initialValue.rating_count_min || 0);
        setAverageRating(initialValue.average_rating || 0);
    }, [initialValue]);

    // Update local filter state after each change
    useEffect(() => {
        const newFilters: MovieFilters = {};

        if (inputValue) {
            newFilters.title = inputValue;
        }
        if (selectedCountries.length > 0) {
            newFilters.countries = selectedCountries.join(',');
        }
        if (selectedYears.length > 0) {
            newFilters.years = selectedYears.join(',');
        }
        if (selectedGenres.length > 0) {
            newFilters.genres = selectedGenres.join(',');
        }
        if (ratingCountMin > 0) {
            newFilters.rating_count_min = ratingCountMin;
        }
        if (averageRating > 0) {
            newFilters.average_rating = averageRating;
        }

        onChange(newFilters);
    }, [inputValue, selectedCountries, selectedYears, selectedGenres, ratingCountMin, averageRating, onChange]);

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

    const handleRatingCountMinChange = (value: number) => {
        setRatingCountMin(value);
    };

    const handleAverageRatingChange = (value: number) => {
        setAverageRating(value);
    };

    const setFiltersDirectly = (filters: MovieFilters) => {
        setInputValue(filters.title || '');
        setSelectedCountries(filters.countries ? filters.countries.split(',') : []);
        setSelectedYears(filters.years ? filters.years.split(',') : []);
        setSelectedGenres(filters.genres ? filters.genres.split(',') : []);
        setRatingCountMin(filters.rating_count_min || 0);
        setAverageRating(filters.average_rating || 0);
    };

    return {
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
    };
};

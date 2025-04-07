// hooks/useMovieFilters.ts
import { useState, useEffect } from 'react';

interface Filters {
    title?: string;
    genres?: string;
    years?: string;
    rating?: string;
}

export const useMovieFilters = (initialFilters: Filters, setLocalFilters: (filters: Filters) => void) => {
    const [inputValue, setInputValue] = useState<string>(initialFilters.title || '');
    const [selectedGenres, setSelectedGenres] = useState<string[]>(
        initialFilters.genres ? initialFilters.genres.split(',') : []
    );
    const [selectedYears, setSelectedYears] = useState<string[]>(
        initialFilters.years ? initialFilters.years.split(',') : []
    );
    const [selectedRating, setSelectedRating] = useState<string>(initialFilters.rating || '');

    useEffect(() => {
        const newFilters: Filters = {};
        if (inputValue) newFilters.title = inputValue;
        if (selectedGenres.length > 0) newFilters.genres = selectedGenres.join(',');
        if (selectedYears.length > 0) newFilters.years = selectedYears.join(',');
        if (selectedRating) newFilters.rating = selectedRating;

        setLocalFilters(newFilters);
    }, [inputValue, selectedGenres, selectedYears, selectedRating, setLocalFilters]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value);
    };

    const handleClear = () => {
        setInputValue('');
    };

    const toggleGenre = (genre: string) => {
        setSelectedGenres(prev =>
            prev.includes(genre)
                ? prev.filter(g => g !== genre)
                : [...prev, genre]
        );
    };

    const toggleYears = (year: string) => {
        setSelectedYears(prev =>
            prev.includes(year)
                ? prev.filter(y => y !== year)
                : [...prev, year]
        );
    };

    const setYearsDirectly = (years: string[]) => {
        setSelectedYears(years);
    };

    const handleRatingChange = (rating: string) => {
        setSelectedRating(prev => prev === rating ? '' : rating);
    };

    const setFiltersDirectly = (filters: Filters) => {
        setInputValue(filters.title || '');
        setSelectedGenres(filters.genres ? filters.genres.split(',') : []);
        setSelectedYears(filters.years ? filters.years.split(',') : []);
        setSelectedRating(filters.rating || '');
    };

    return {
        inputValue,
        selectedGenres,
        selectedYears,
        selectedRating,
        handleInputChange,
        handleClear,
        toggleGenre,
        toggleYears,
        setYearsDirectly,
        handleRatingChange,
        setFiltersDirectly
    };
};

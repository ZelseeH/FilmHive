import { useState, useEffect, Dispatch, SetStateAction } from 'react';

interface Filters {
    name?: string;
    countries?: string;
    years?: string;
    gender?: string;
    type?: 'actor' | 'director';
}

export const usePeopleFilters = (
    initialValue: Filters,
    onChange: ((filters: Filters) => void) | Dispatch<SetStateAction<Filters>>
) => {
    const [inputValue, setInputValue] = useState<string>(initialValue.name || '');
    const [selectedCountries, setSelectedCountries] = useState<string[]>(
        initialValue.countries ? initialValue.countries.split(',') : []
    );
    const [selectedYears, setSelectedYears] = useState<string[]>(
        initialValue.years ? initialValue.years.split(',') : []
    );
    const [selectedGender, setSelectedGender] = useState<string>(initialValue.gender || '');
    const [selectedType, setSelectedType] = useState<'actor' | 'director' | ''>(
        initialValue.type || ''
    );

    useEffect(() => {
        setInputValue(initialValue.name || '');
        setSelectedCountries(initialValue.countries ? initialValue.countries.split(',') : []);
        setSelectedYears(initialValue.years ? initialValue.years.split(',') : []);
        setSelectedGender(initialValue.gender || '');
        setSelectedType(initialValue.type || '');
    }, [initialValue]);

    useEffect(() => {
        const newFilters: Filters = {};

        if (inputValue) {
            newFilters.name = inputValue;
        }

        if (selectedCountries.length > 0) {
            newFilters.countries = selectedCountries.join(',');
        }

        if (selectedYears.length > 0) {
            newFilters.years = selectedYears.join(',');
        }

        if (selectedGender) {
            newFilters.gender = selectedGender;
        }

        if (selectedType) {
            newFilters.type = selectedType;
        }

        // Handle both function and state setter
        if (typeof onChange === 'function') {
            onChange(newFilters);
        }
    }, [inputValue, selectedCountries, selectedYears, selectedGender, selectedType, onChange]);

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

    const toggleYears = (years: string[]) => {
        if (years.length === 1) {
            const year = years[0];
            setSelectedYears(prev =>
                prev.includes(year)
                    ? prev.filter(y => y !== year)
                    : [...prev, year]
            );
        } else {
            const allSelected = years.every(year => selectedYears.includes(year));

            if (allSelected) {
                setSelectedYears(prev => prev.filter(year => !years.includes(year)));
            } else {
                setSelectedYears(prev => {
                    const existingYears = new Set(prev);
                    years.forEach(year => existingYears.add(year));
                    return Array.from(existingYears);
                });
            }
        }
    };

    const setYearsDirectly = (years: string[]) => {
        setSelectedYears(years);
    };

    const handleGenderChange = (gender: string) => {
        setSelectedGender(prev => prev === gender ? '' : gender);
    };

    const handleTypeChange = (type: 'actor' | 'director') => {
        setSelectedType(prev => prev === type ? '' : type);
    };

    const setFiltersDirectly = (filters: Filters) => {
        setInputValue(filters.name || '');
        setSelectedCountries(filters.countries ? filters.countries.split(',') : []);
        setSelectedYears(filters.years ? filters.years.split(',') : []);
        setSelectedGender(filters.gender || '');
        setSelectedType(filters.type || '');
    };

    return {
        inputValue,
        selectedCountries,
        selectedYears,
        selectedGender,
        selectedType,
        handleInputChange,
        handleClear,
        toggleCountry,
        toggleYears,
        setYearsDirectly,
        handleGenderChange,
        handleTypeChange,
        setFiltersDirectly
    };
};

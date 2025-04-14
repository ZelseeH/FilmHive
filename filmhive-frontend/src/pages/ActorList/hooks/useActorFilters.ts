import { useState, useEffect } from 'react';

interface Filters {
    name?: string;
    countries?: string;
    years?: string;
    gender?: string;
}

export const useActorFilters = (initialValue: Filters, onChange: (filters: Filters) => void) => {
    const [inputValue, setInputValue] = useState<string>(initialValue.name || '');
    const [selectedCountries, setSelectedCountries] = useState<string[]>(
        initialValue.countries ? initialValue.countries.split(',') : []
    );
    const [selectedYears, setSelectedYears] = useState<string[]>(
        initialValue.years ? initialValue.years.split(',') : []
    );
    const [selectedGender, setSelectedGender] = useState<string>(initialValue.gender || '');

    useEffect(() => {
        setInputValue(initialValue.name || '');
        setSelectedCountries(initialValue.countries ? initialValue.countries.split(',') : []);
        setSelectedYears(initialValue.years ? initialValue.years.split(',') : []);
        setSelectedGender(initialValue.gender || '');
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

        onChange(newFilters);
    }, [inputValue, selectedCountries, selectedYears, selectedGender, onChange]);

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

    const setFiltersDirectly = (filters: Filters) => {
        setInputValue(filters.name || '');
        setSelectedCountries(filters.countries ? filters.countries.split(',') : []);
        setSelectedYears(filters.years ? filters.years.split(',') : []);
        setSelectedGender(filters.gender || '');
    };

    return {
        inputValue,
        selectedCountries,
        selectedYears,
        selectedGender,
        handleInputChange,
        handleClear,
        toggleCountry,
        toggleYears,
        setYearsDirectly,
        handleGenderChange,
        setFiltersDirectly
    };
};

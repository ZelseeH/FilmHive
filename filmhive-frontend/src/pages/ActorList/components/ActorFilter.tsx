import React, { useState, useEffect } from 'react';
import styles from './ActorFilter.module.css';
import { useActorFilters } from '../hooks/useActorFilters';
import { useBirthplaces } from '../hooks/useBirthplaces';
import { useYearsRange } from '../hooks/useYearsRange';
import SearchInput from './SearchInput';
import CountryFilter from './CountryFilter';
import YearFilter from './YearFilter';
import GenderFilter from './GenderFilter';
import { IoMdClose } from 'react-icons/io';

interface Filters {
    name?: string;
    countries?: string;
    years?: string;
    gender?: string;
}

interface ActorFilterProps {
    value: Filters;
    onChange: (filters: Filters) => void;
    onClose?: () => void;
}

const ActorFilter: React.FC<ActorFilterProps> = ({ value, onChange, onClose }) => {
    const [localFilters, setLocalFilters] = useState<Filters>(value);

    const {
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
    } = useActorFilters(value, setLocalFilters);

    const { countries, isLoadingCountries } = useBirthplaces();
    const {
        showAllYears,
        displayedYears,
        handleShowAllYears,
        handleShowLessYears
    } = useYearsRange();

    const genders = [
        { value: 'M', label: 'Mężczyzna' },
        { value: 'K', label: 'Kobieta' }
    ];

    const prepareFilters = (): Filters => {
        const filters: Filters = {};
        if (inputValue) filters.name = inputValue;
        if (selectedCountries.length > 0) filters.countries = selectedCountries.join(',');
        if (selectedYears.length > 0) filters.years = selectedYears.join(',');
        if (selectedGender) filters.gender = selectedGender;
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

                <GenderFilter
                    genders={genders}
                    selectedGender={selectedGender}
                    onToggle={handleGenderChange}
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

export default ActorFilter;

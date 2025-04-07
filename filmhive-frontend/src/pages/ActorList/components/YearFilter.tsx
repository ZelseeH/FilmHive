import React, { useState } from 'react';
import styles from './FilterOptions.module.css';

interface YearFilterProps {
    years: string[];
    selectedYears: string[];
    showAllYears: boolean;
    onToggle: (years: string[]) => void;
    onForceSelect: (years: string[]) => void;
    onShowAll: () => void;
    onShowLess?: () => void;
}

const YearFilter: React.FC<YearFilterProps> = ({
    years,
    selectedYears,
    showAllYears,
    onToggle,
    onForceSelect,
    onShowAll,
    onShowLess
}) => {
    const [lastSelectedYear, setLastSelectedYear] = useState<string | null>(null);
    const [selectionState, setSelectionState] = useState<'new' | 'single' | 'range'>('new');

    const handleYearToggle = (year: string) => {
        switch (selectionState) {
            case 'new':
                setLastSelectedYear(year);
                setSelectionState('single');
                onToggle([year]);
                break;

            case 'single':
                if (year === lastSelectedYear) {
                    onToggle([year]);
                } else {
                    const startIndex = years.indexOf(lastSelectedYear!);
                    const endIndex = years.indexOf(year);
                    const range = years.slice(
                        Math.min(startIndex, endIndex),
                        Math.max(startIndex, endIndex) + 1
                    );
                    setSelectionState('range');
                    onToggle(range);
                }
                break;

            case 'range':
                // Trzeci klik – nowy pojedynczy wybór, bez toggle
                setLastSelectedYear(year);
                setSelectionState('single');
                onForceSelect([year]);
                break;
        }
    };

    return (
        <div className={styles.filterSection}>
            <h3>Data urodzenia</h3>
            <div className={styles.filterOptions}>
                {years.map(year => (
                    <button
                        key={year}
                        className={`${styles.filterOption} ${selectedYears.includes(year) ? styles.selected : ''}`}
                        onClick={() => handleYearToggle(year)}
                    >
                        {year}
                    </button>
                ))}
            </div>
            {!showAllYears ? (
                <button className={styles.showAllButton} onClick={onShowAll}>
                    Pokaż wszystkie
                </button>
            ) : (
                <button className={styles.showAllButton} onClick={onShowLess}>
                    Pokaż mniej
                </button>
            )}
        </div>
    );
};

export default YearFilter;

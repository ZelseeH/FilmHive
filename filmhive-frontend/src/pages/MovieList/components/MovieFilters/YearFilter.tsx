import React, { useState } from 'react';
import styles from './YearFilter.module.css';

interface YearFilterProps {
    years: string[];
    selectedYears: string[];
    showAllYears: boolean;
    onToggle: (year: string) => void;
    onForceSelect: (years: string[]) => void;
    onShowAll: () => void;
    onShowLess: () => void;
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
                onForceSelect([year]);
                break;

            case 'single':
                if (year === lastSelectedYear) {
                    // Drugi klik na ten sam rok - pozostajemy w stanie 'single'
                    onToggle(year);
                } else {
                    // Drugi klik na inny rok - tworzymy zakres
                    const startIndex = years.indexOf(lastSelectedYear!);
                    const endIndex = years.indexOf(year);
                    const range = years.slice(
                        Math.min(startIndex, endIndex),
                        Math.max(startIndex, endIndex) + 1
                    );
                    setSelectionState('range');
                    onForceSelect(range);
                }
                break;

            case 'range':
                // Trzeci klik – nowy pojedynczy wybór
                setLastSelectedYear(year);
                setSelectionState('single');
                onForceSelect([year]);
                break;
        }
    };

    return (
        <div className={styles.filterSection}>
            <h3>Rok produkcji</h3>
            <div className={styles.yearList}>
                {years.map(year => (
                    <div
                        key={year}
                        className={`${styles.yearItem} ${selectedYears.includes(year) ? styles.selected : ''}`}
                        onClick={() => handleYearToggle(year)}
                    >
                        {year}
                    </div>
                ))}
            </div>
            {years.length > 10 && (
                <button
                    className={styles.showMoreButton}
                    onClick={showAllYears ? onShowLess : onShowAll}
                >
                    {showAllYears ? 'Pokaż mniej' : 'Pokaż wszystkie lata'}
                </button>
            )}
        </div>
    );
};

export default YearFilter;

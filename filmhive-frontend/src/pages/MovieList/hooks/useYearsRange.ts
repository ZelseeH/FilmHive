// hooks/useYearsRange.ts
import { useState, useEffect, useCallback } from 'react';

export const useYearsRange = () => {
    const [years, setYears] = useState<string[]>([]);
    const [displayedYears, setDisplayedYears] = useState<string[]>([]);
    const [showAllYears, setShowAllYears] = useState<boolean>(false);

    useEffect(() => {
        const generateYears = () => {
            const currentYear = new Date().getFullYear();
            const yearsArray = [];
            for (let year = currentYear; year >= 1900; year--) {
                yearsArray.push(year.toString());
            }
            setYears(yearsArray);
            setDisplayedYears(yearsArray.slice(0, 15));
        };

        generateYears();
    }, []);

    const handleShowAllYears = useCallback(() => {
        setDisplayedYears(years);
        setShowAllYears(true);
    }, [years]);

    const handleShowLessYears = useCallback(() => {
        setDisplayedYears(years.slice(0, 15));
        setShowAllYears(false);
    }, [years]);

    return {
        years,
        displayedYears,
        showAllYears,
        handleShowAllYears,
        handleShowLessYears
    };
};

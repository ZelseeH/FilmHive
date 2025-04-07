import { useState, useEffect } from 'react';

export const useYearsRange = () => {
    const [showAllYears, setShowAllYears] = useState<boolean>(false);
    const [allYears, setAllYears] = useState<string[]>([]);
    const [displayedYears, setDisplayedYears] = useState<string[]>([]);

    useEffect(() => {
        const generateYears = () => {
            const currentYear = new Date().getFullYear();
            const years = [];
            for (let year = currentYear; year >= 1900; year--) {
                years.push(year.toString());
            }
            setAllYears(years);
            setDisplayedYears(years.slice(0, 15));
        };

        generateYears();
    }, []);

    const handleShowAllYears = () => {
        setShowAllYears(true);
        setDisplayedYears(allYears);
    };

    const handleShowLessYears = () => {
        setShowAllYears(false);
        setDisplayedYears(allYears.slice(0, 15));
    };

    return {
        showAllYears,
        displayedYears,
        handleShowAllYears,
        handleShowLessYears
    };
};

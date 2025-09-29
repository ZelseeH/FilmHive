import { useRef, useState, useEffect, useCallback } from 'react';

export function useSlider(scrollAmount: number) {
    const sliderRef = useRef<HTMLDivElement>(null);
    const [disableLeft, setDisableLeft] = useState(true);
    const [disableRight, setDisableRight] = useState(false);

    const updateButtonsState = useCallback(() => {
        if (!sliderRef.current) return;
        const { scrollLeft, scrollWidth, clientWidth } = sliderRef.current;
        setDisableLeft(scrollLeft <= 0);
        setDisableRight(scrollLeft + clientWidth >= scrollWidth);
    }, []);

    useEffect(() => {
        updateButtonsState();
        const current = sliderRef.current;
        if (!current) return;
        current.addEventListener('scroll', updateButtonsState);
        return () => current.removeEventListener('scroll', updateButtonsState);
    }, [updateButtonsState]);

    const scrollLeftFn = () => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        }
    };

    const scrollRightFn = () => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
    };

    return {
        sliderRef,
        scrollLeft: scrollLeftFn,
        scrollRight: scrollRightFn,
        disableLeft,
        disableRight,
    };
}

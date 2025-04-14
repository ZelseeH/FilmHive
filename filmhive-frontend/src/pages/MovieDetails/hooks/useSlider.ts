import { useRef, useCallback } from 'react';

export const useSlider = (scrollAmount: number = 200) => {
    const sliderRef = useRef<HTMLDivElement | null>(null);

    const scrollLeft = useCallback(() => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        }
    }, [scrollAmount]);

    const scrollRight = useCallback(() => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
    }, [scrollAmount]);

    return { sliderRef, scrollLeft, scrollRight };
};

import { useEffect, useRef } from 'react';

export const useScrollLock = (isLocked: boolean) => {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;

        if (isLocked) {
            document.body.style.overflow = 'hidden';
            document.body.style.paddingRight = `${scrollbarWidth}px`;
            if (containerRef.current) {
                containerRef.current.style.paddingRight = `${scrollbarWidth}px`;
            }
        } else {
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            if (containerRef.current) {
                containerRef.current.style.paddingRight = '';
            }
        }

        return () => {
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            if (containerRef.current) {
                containerRef.current.style.paddingRight = '';
            }
        };
    }, [isLocked]);

    return containerRef;
};

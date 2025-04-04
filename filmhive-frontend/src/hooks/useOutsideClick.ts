import { useEffect, RefObject } from 'react';

/**

 * @param ref
 * @param callback 
 * @param excludeRef 
 */
export const useOutsideClick = (
    ref: RefObject<HTMLElement | null>,
    callback: () => void,
    excludeRef?: RefObject<HTMLElement | null>
): void => {
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent | TouchEvent) => {
            const target = event.target as Node;

            if (
                ref.current &&
                !ref.current.contains(target) &&
                (!excludeRef || !excludeRef.current?.contains(target))
            ) {
                callback();
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('touchstart', handleClickOutside);

        return () => {

            document.removeEventListener('mousedown', handleClickOutside);
            document.removeEventListener('touchstart', handleClickOutside);
        };
    }, [ref, excludeRef, callback]);
};

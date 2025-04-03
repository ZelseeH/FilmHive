import { useEffect, RefObject } from 'react';

/**
 * Hook `useOutsideClick` wykrywa kliknięcia poza określonym elementem.
 * @param ref - Referencja do elementu, dla którego chcemy wykryć kliknięcia na zewnątrz.
 * @param callback - Funkcja wywoływana po kliknięciu poza elementem.
 * @param excludeRef - Opcjonalna referencja do elementu, który ma być wykluczony z wykrywania.
 */
export const useOutsideClick = (
    ref: RefObject<HTMLElement | null>,
    callback: () => void,
    excludeRef?: RefObject<HTMLElement | null>
): void => {
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent | TouchEvent) => {
            const target = event.target as Node;

            // Sprawdź, czy kliknięcie było poza elementami ref i excludeRef
            if (
                ref.current &&
                !ref.current.contains(target) &&
                (!excludeRef || !excludeRef.current?.contains(target))
            ) {
                callback();
            }
        };

        // Dodaj nasłuchiwacze dla zdarzeń `mousedown` i `touchstart`
        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('touchstart', handleClickOutside);

        return () => {
            // Usuń nasłuchiwacze po odmontowaniu komponentu
            document.removeEventListener('mousedown', handleClickOutside);
            document.removeEventListener('touchstart', handleClickOutside);
        };
    }, [ref, excludeRef, callback]);
};

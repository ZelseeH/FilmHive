/**
 * Oblicza pozycję menu użytkownika względem elementu referencyjnego (np. avatara)
 * @param element Element referencyjny, względem którego pozycjonowane jest menu
 * @returns Obiekt zawierający współrzędne top i left dla menu
 */
export const calculateMenuPosition = (element: HTMLElement | null): { top: number; left: number } => {
    if (element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const top = rect.bottom;

        return { top, left: centerX };
    }

    // Domyślna pozycja, gdy element referencyjny nie istnieje
    return { top: 60, left: window.innerWidth - 100 };
};

/**
 * Sprawdza, czy kliknięcie nastąpiło w określony element lub jego potomków
 * @param target Element, który został kliknięty
 * @param selector Selektor CSS elementu, który chcemy sprawdzić
 * @returns true, jeśli kliknięcie nastąpiło w element lub jego potomków, false w przeciwnym przypadku
 */
export const isClickInsideElement = (target: HTMLElement, selector: string): boolean => {
    return !!target.closest(selector);
};

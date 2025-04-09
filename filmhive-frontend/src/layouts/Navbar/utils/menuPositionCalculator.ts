/**
 * @param element 
 * @returns
 */
export const calculateMenuPosition = (element: HTMLElement | null): { top: number; left: number } => {
    if (element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const top = rect.bottom;

        return { top, left: centerX };
    }


    return { top: 60, left: window.innerWidth - 100 };
};

/**
 * @param target 
 * @param selector 
 * @returns 
 */
export const isClickInsideElement = (target: HTMLElement, selector: string): boolean => {
    return !!target.closest(selector);
};

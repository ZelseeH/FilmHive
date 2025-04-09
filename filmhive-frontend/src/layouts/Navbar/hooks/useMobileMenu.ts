// hooks/useMobileMenu.ts
import { useState } from 'react';

export const useMobileMenu = () => {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const toggleMobileMenu = () => {
        setMobileMenuOpen(!mobileMenuOpen);
    };

    const closeMobileMenu = () => {
        setMobileMenuOpen(false);
    };

    return {
        mobileMenuOpen,
        toggleMobileMenu,
        closeMobileMenu
    };
};

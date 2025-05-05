
import { useState, useRef } from 'react';
import { calculateMenuPosition } from '../utils/menuPositionCalculator';

export const useUserMenuPosition = () => {
    const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
    const userMenuRef = useRef<HTMLDivElement>(null);
    const userSectionRef = useRef<HTMLDivElement>(null);

    const toggleUserMenu = () => setIsUserMenuOpen(prev => !prev);
    const closeUserMenu = () => setIsUserMenuOpen(false);

    const getUserMenuPosition = () => {
        return calculateMenuPosition(userSectionRef.current);
    };

    return {
        isUserMenuOpen,
        setIsUserMenuOpen,
        toggleUserMenu,
        closeUserMenu,
        userMenuRef,
        userSectionRef,
        getUserMenuPosition
    };
};

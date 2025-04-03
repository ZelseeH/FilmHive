// hooks/useUserMenu.ts
import { useState, useRef, useEffect } from 'react';
import { calculateMenuPosition, isClickInsideElement } from '../utils/menuPositionCalculator';

export const useUserMenu = () => {
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0 });
    const avatarRef = useRef<HTMLDivElement>(null);

    const toggleUserMenu = (e: React.MouseEvent) => {
        e.stopPropagation();
        const newPosition = calculateMenuPosition(avatarRef.current);
        setMenuPosition(newPosition);
        setShowUserMenu(!showUserMenu);
    };

    const closeUserMenu = () => {
        setShowUserMenu(false);
    };

    useEffect(() => {
        const handleGlobalClick = (e: MouseEvent) => {
            const target = e.target as HTMLElement;
            const isAvatarClick = isClickInsideElement(target, '#user-avatar');
            const isMenuClick = isClickInsideElement(target, '.user-menu');

            if (showUserMenu && !isAvatarClick && !isMenuClick) {
                closeUserMenu();
            }
        };

        const handleResize = () => {
            if (showUserMenu) {
                const newPosition = calculateMenuPosition(avatarRef.current);
                setMenuPosition(newPosition);
            }
        };

        window.addEventListener('click', handleGlobalClick);
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('click', handleGlobalClick);
            window.removeEventListener('resize', handleResize);
        };
    }, [showUserMenu]);

    return {
        showUserMenu,
        menuPosition,
        avatarRef,
        toggleUserMenu,
        closeUserMenu
    };
};

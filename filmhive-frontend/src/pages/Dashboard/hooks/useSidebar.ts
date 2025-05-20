import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../../../contexts/AuthContext';
import { SubMenuItem } from './types'; // Załóżmy, że przeniesiesz typy do osobnego pliku

export const useSidebar = (collapsed: boolean, toggleSidebar: () => void) => {
    const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});
    const [isMobile, setIsMobile] = useState(false);
    const location = useLocation();
    const { user, isAdmin, isModerator } = useAuth();

    // Sprawdź czy jest to widok mobilny
    useEffect(() => {
        const checkMobile = () => {
            setIsMobile(window.innerWidth <= 992);
        };

        checkMobile();
        window.addEventListener('resize', checkMobile);

        return () => window.removeEventListener('resize', checkMobile);
    }, []);

    // Automatyczne zwijanie submenu gdy sidebar jest zwinięty
    useEffect(() => {
        if (collapsed) {
            setExpandedItems({});
        }
    }, [collapsed]);

    const toggleSubmenu = (label: string, e: React.MouseEvent) => {
        e.preventDefault();

        // Jeśli sidebar jest zwinięty, najpierw go rozwiń
        if (collapsed) {
            toggleSidebar();

            // Opóźnij rozwinięcie submenu, aby dać czas na animację sidebara
            setTimeout(() => {
                setExpandedItems(prev => ({
                    ...prev,
                    [label]: true
                }));
            }, 300); // Czas powinien odpowiadać czasowi animacji sidebara
        } else {
            // Normalnie przełącz stan submenu
            setExpandedItems(prev => ({
                ...prev,
                [label]: !prev[label]
            }));
        }
    };

    const isActive = (path?: string) => {
        if (!path) return false;
        return location.pathname === path || location.pathname.startsWith(path + '/');
    };

    const isSubmenuActive = (subItems?: SubMenuItem[]) => {
        if (!subItems) return false;
        return subItems.some(item => isActive(item.path));
    };

    return {
        expandedItems,
        isMobile,
        user,
        isAdmin,
        isModerator,
        toggleSubmenu,
        isActive,
        isSubmenuActive
    };
};

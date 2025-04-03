import { useState, useRef, useEffect } from 'react';

export const useNavbarMenu = () => {
    const [isOpen, setIsOpen] = useState(false);
    const hamburgerRef = useRef<HTMLDivElement>(null);
    const mobileMenuRef = useRef<HTMLDivElement>(null);
    const prevScrollYRef = useRef<number>(0);

    const toggleMenu = () => setIsOpen(prev => !prev);
    const closeMobileMenu = () => setIsOpen(false);

    useEffect(() => {
        const handleScroll = () => {
            if (isOpen) {
                const scrollY = window.scrollY;
                const prevScrollY = prevScrollYRef.current;
                if (scrollY > prevScrollY) {
                    closeMobileMenu();
                }
                prevScrollYRef.current = scrollY;
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [isOpen]);

    return {
        isOpen,
        setIsOpen,
        toggleMenu,
        closeMobileMenu,
        hamburgerRef,
        mobileMenuRef,
        prevScrollYRef
    };
};

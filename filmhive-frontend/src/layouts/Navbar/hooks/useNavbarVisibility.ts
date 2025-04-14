import { useState, useEffect } from 'react';

export const useNavbarVisibility = () => {
    const [show, setShow] = useState<boolean>(true);
    const [lastScrollY, setLastScrollY] = useState<number>(0);

    const controlNavbar = () => {
        const isMobile = window.innerWidth <= 992;
        const currentScrollY = window.scrollY;

        if (isMobile) {
            if (currentScrollY > lastScrollY && currentScrollY > 60) {
                setShow(false);
            } else {
                setShow(true);
            }
            setLastScrollY(currentScrollY);
        } else {
            setShow(true);
        }
    };

    useEffect(() => {
        window.addEventListener('scroll', controlNavbar);
        return () => {
            window.removeEventListener('scroll', controlNavbar);
        };
    }, [lastScrollY]);

    return { show };
};

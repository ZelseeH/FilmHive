import React, { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

const ScrollAnchor: React.FC = () => {
    const location = useLocation();
    const lastHash = useRef('');

    useEffect(() => {
        console.log('🔍 ScrollAnchor - Location changed:', location.pathname, location.hash);

        if (location.hash) {
            lastHash.current = location.hash.slice(1); // usuń # z początku
            console.log('🔍 ScrollAnchor - Hash found:', lastHash.current);
        }

        if (lastHash.current && document.getElementById(lastHash.current)) {
            console.log('🔍 ScrollAnchor - Element found, scrolling to:', lastHash.current);
            setTimeout(() => {
                const element = document.getElementById(lastHash.current);
                if (element) {
                    element.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    console.log('🔍 ScrollAnchor - Scrolled to element');
                }
                lastHash.current = '';
            }, 500); // Zwiększ delay do 500ms
        } else if (lastHash.current) {
            console.log('🔍 ScrollAnchor - Element NOT found:', lastHash.current);
        }
    }, [location]);

    return null;
};

export default ScrollAnchor;

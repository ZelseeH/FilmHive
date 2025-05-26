import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ThemeContextType {
    isDarkMode: boolean;
    toggleTheme: () => void;
    setTheme: (dark: boolean) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within ThemeProvider');
    }
    return context;
};

interface ThemeProviderProps {
    children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
    const [isDarkMode, setIsDarkMode] = useState<boolean>(false);

    useEffect(() => {
        // Załaduj motyw z localStorage
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            const dark = savedTheme === 'dark';
            setIsDarkMode(dark);
            applyTheme(dark);
        }
    }, []);

    const applyTheme = (dark: boolean) => {
        if (dark) {
            document.body.classList.add('dark-theme');
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.body.classList.remove('dark-theme');
            document.documentElement.setAttribute('data-theme', 'light');
        }
    };

    const setTheme = (dark: boolean) => {
        setIsDarkMode(dark);
        localStorage.setItem('theme', dark ? 'dark' : 'light');
        applyTheme(dark);
    };

    const toggleTheme = () => {
        setTheme(!isDarkMode);
    };

    return (
        <ThemeContext.Provider value={{ isDarkMode, toggleTheme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

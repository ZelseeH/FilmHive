// services/navbarService.ts
import { NavigateFunction } from 'react-router-dom';

/**
 * Obsługuje proces wylogowania użytkownika
 * @param logout Funkcja wylogowująca z kontekstu autoryzacji
 * @param closeUserMenu Funkcja zamykająca menu użytkownika
 * @param navigate Funkcja nawigacji z React Router
 */
export const handleLogout = (
    logout: () => void,
    closeUserMenu: () => void,
    navigate: NavigateFunction
) => {
    closeUserMenu();
    logout();
    navigate('/');
};

/**
 * Sprawdza, czy użytkownik jest zalogowany
 * @param user Obiekt użytkownika z kontekstu autoryzacji
 * @returns true, jeśli użytkownik jest zalogowany, false w przeciwnym przypadku
 */
export const isUserLoggedIn = (user: any): boolean => {
    return !!user;
};

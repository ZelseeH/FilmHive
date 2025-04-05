import { NavigateFunction } from 'react-router-dom';

/**

 * @param logout 
 * @param closeUserMenu 
 * @param navigate 
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
 * @param user 
 * @returns 
 */
export const isUserLoggedIn = (user: any): boolean => {
    return !!user;
};

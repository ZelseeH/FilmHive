import { fetchWithAuth } from '../../../services/api';

interface LoginResponse {
    user: any;
    access_token: string;
    refresh_token: string;
}

export const login = async (username: string, password: string): Promise<LoginResponse> => {
    try {
        return await fetchWithAuth('auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    } catch (error: any) {
        // Przekazujemy oryginalny błąd, aby LoginModal mógł sprawdzić status HTTP
        console.error('Login error in authService:', error);
        throw error;
    }
};

export const register = async (username: string, email: string, password: string): Promise<LoginResponse> => {
    try {
        return await fetchWithAuth('auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    } catch (error: any) {
        // Przekazujemy oryginalny błąd, aby LoginModal mógł sprawdzić status HTTP
        console.error('Register error in authService:', error);
        throw error;
    }
};

// services/authService.ts
import { fetchWithAuth } from './api';

interface LoginResponse {
    user: any;
    access_token: string;
}

export const login = async (username: string, password: string): Promise<LoginResponse> => {
    return fetchWithAuth('auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
};

export const register = async (username: string, email: string, password: string): Promise<LoginResponse> => {
    return fetchWithAuth('auth/register', {
        method: 'POST',
        body: JSON.stringify({ username, email, password })
    });
};

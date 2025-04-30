import { fetchWithAuth } from '../../../services/api';

// Typ zgodny z backendem Marshmallow
export interface User {
    user_id: number;
    username: string;
    email: string;
    name?: string;
    bio?: string;
    profile_picture?: string;
    registration_date?: string;
    background_image?: string;
    background_position?: { x: number; y: number };
    role?: number;
    // Dodaj inne pola jeśli są potrzebne
}

export interface LoginResponse {
    user: User;
    access_token: string;
    error?: string;
}

export const login = async (username: string, password: string): Promise<LoginResponse> => {
    const response = await fetchWithAuth('auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
        headers: { 'Content-Type': 'application/json' }
    });

    if (response.error) {
        throw new Error(response.error);
    }
    if (!response.access_token || !response.user) {
        throw new Error("Brak tokenu lub użytkownika w odpowiedzi");
    }

    return response;
};

export const register = async (username: string, email: string, password: string): Promise<LoginResponse> => {
    const response = await fetchWithAuth('auth/register', {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
        headers: { 'Content-Type': 'application/json' }
    });

    if (response.error) {
        throw new Error(response.error);
    }
    if (!response.access_token || !response.user) {
        throw new Error("Brak tokenu lub użytkownika w odpowiedzi");
    }

    return response;
};

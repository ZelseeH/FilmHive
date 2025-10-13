import { clearAuthAndCache } from '../services/api';  // Import (path dostosuj do struktury, np. '../../../services/api')

interface ValidationResult {
    valid: boolean;
    error: string;
}

export const authUtils = {
    getToken: (): string | null => {
        return localStorage.getItem('accessToken');  // Zmień z 'token' na 'accessToken' (standard z AuthContext)
    },

    isAuthenticated: (): boolean => {
        const token = localStorage.getItem('accessToken');  // Zmień na 'accessToken'
        return !!token && token.length > 0;  // Podstawowy check (bez expiry decode)
    },

    // Nowy: logout (z call clearAuthAndCache dla consistency)
    logout: (): void => {
        clearAuthAndCache();  // Clear tokens/cache
        // Opcjonalnie: Redirect jeśli w utils, ale lepiej w context/component
    },

    validatePassword: (password: string, confirmPassword: string): ValidationResult => {
        if (password !== confirmPassword) {
            return { valid: false, error: 'Hasła nie są identyczne.' };
        }
        return { valid: true, error: '' };
    },

    validateRequiredField: (value: string, fieldName: string): ValidationResult => {
        if (!value || value.trim() === '') {
            return { valid: false, error: `Pole ${fieldName} jest wymagane.` };
        }
        return { valid: true, error: '' };
    }
};

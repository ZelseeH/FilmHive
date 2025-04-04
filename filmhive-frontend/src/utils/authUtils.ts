// Define an interface for validation result
interface ValidationResult {
    valid: boolean;
    error: string;
}

export const authUtils = {
    getToken: (): string | null => {
        return localStorage.getItem('token');
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

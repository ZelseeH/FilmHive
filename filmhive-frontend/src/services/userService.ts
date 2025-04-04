import { authUtils } from '../utils/authUtils';

// Define interfaces for the data structures
interface ProfileData {
    name?: string;
    bio?: string;
    [key: string]: any; // For any additional fields
}

export const userService = {
    getUserProfile: async () => {
        const token = authUtils.getToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego. Zaloguj się ponownie.');
        }

        const response = await fetch('http://localhost:5000/api/user/profile', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Nie udało się pobrać danych użytkownika.');
        }

        return await response.json();
    },

    updateProfile: async (data: ProfileData) => {
        const token = authUtils.getToken();
        const response = await fetch('http://localhost:5000/api/user/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Nie udało się zaktualizować profilu.');
        }

        return await response.json();
    },

    updateEmail: async (email: string, currentPassword: string) => {
        const token = authUtils.getToken();
        const response = await fetch('http://localhost:5000/api/user/update-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                email,
                current_password: currentPassword
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Nie udało się zmienić adresu email.');
        }

        return await response.json();
    },

    changePassword: async (currentPassword: string, newPassword: string) => {
        const token = authUtils.getToken();
        const response = await fetch('http://localhost:5000/api/auth/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Nie udało się zmienić hasła.');
        }

        return await response.json();
    }
};

// services/userService.ts
interface UserData {
    id: string;
    username: string;
    name: string;
    email: string;
    role: number;
    is_active: boolean;
    registration_date: string;
    last_login?: string;
    profile_picture?: string;
    background_image?: string;
    bio?: string;
}

interface CreateUserData {
    username: string;
    email: string;
    password: string;
    name?: string;
    bio?: string;
    role?: number;
    is_active?: boolean;
}

// Funkcja pomocnicza do pobierania tokenu
const getAuthToken = (): string | null => {
    return localStorage.getItem('accessToken');
};

export const userService = {
    async getUserDetails(userId: string): Promise<UserData> {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        const response = await fetch(`http://localhost:5000/api/admin/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Nie udało się pobrać szczegółów użytkownika');
        }

        return await response.json();
    },

    async updateUserField(userId: string, fieldName: string, value: any): Promise<UserData> {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        const data = { [fieldName]: value };

        const response = await fetch(`http://localhost:5000/api/admin/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się zaktualizować danych użytkownika');
        }

        return await response.json();
    },

    async updateUserPassword(userId: string, newPassword: string): Promise<void> {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        const response = await fetch(`http://localhost:5000/api/admin/users/${userId}/password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ password: newPassword })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się zmienić hasła użytkownika');
        }
    },

    async updateUserRole(userId: string, role: number): Promise<UserData> {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        const response = await fetch(`http://localhost:5000/api/admin/users/${userId}/role`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ role })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się zmienić roli użytkownika');
        }

        return await response.json();
    },

    async updateUserStatus(userId: string, isActive: boolean): Promise<UserData> {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        const response = await fetch(`http://localhost:5000/api/admin/users/${userId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ is_active: isActive })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się zmienić statusu użytkownika');
        }

        return await response.json();
    },

    // Nowa funkcja do usuwania użytkownika
    async deleteUser(userId: string): Promise<{ message: string; user: UserData }> {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        const response = await fetch(`http://localhost:5000/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się usunąć użytkownika');
        }

        return await response.json();
    },

    // Nowa funkcja do tworzenia użytkownika
    async createUser(userData: CreateUserData): Promise<{ message: string; user: UserData }> {
        const token = getAuthToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego');
        }

        const response = await fetch(`http://localhost:5000/api/admin/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Nie udało się utworzyć użytkownika');
        }

        return await response.json();
    }
};

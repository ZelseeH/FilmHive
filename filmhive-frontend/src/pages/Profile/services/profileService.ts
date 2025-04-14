import { authUtils } from '../../../utils/authUtils';

export interface ProfileData {
    id: string;
    username: string;
    name?: string;
    bio?: string;
    profile_picture?: string;
    background_image?: string;
    background_position?: {
        x: number;
        y: number;
    };
    registration_date?: string;
}

export const profileService = {
    updateBio: async (bio: string, token: string): Promise<void> => {
        const response = await fetch('http://localhost:5000/api/user/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ bio })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Nie udało się zaktualizować opisu.');
        }
    },

    getUserProfile: async (username: string): Promise<ProfileData> => {
        const response = await fetch(`http://localhost:5000/api/user/profile/${username}`);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Nie udało się pobrać danych profilu');
        }

        const rawData = await response.json();
        return rawData;
    }
    ,
    uploadProfilePicture: async (file: File): Promise<string> => {
        const token = authUtils.getToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego. Zaloguj się ponownie.');
        }

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:5000/api/user/profile-picture', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Nie udało się przesłać zdjęcia profilowego.');
        }

        const data = await response.json();
        return data.profile_picture;
    },

    uploadBackgroundImage: async (file: File, position: { x: number, y: number }): Promise<string> => {
        const token = authUtils.getToken();
        if (!token) {
            throw new Error('Brak tokenu autoryzacyjnego. Zaloguj się ponownie.');
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('position_x', position.x.toString());
        formData.append('position_y', position.y.toString());


        const response = await fetch('http://localhost:5000/api/user/background-image', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Nie udało się przesłać zdjęcia w tle.');
        }

        const data = await response.json();
        return data.background_image;
    }

};

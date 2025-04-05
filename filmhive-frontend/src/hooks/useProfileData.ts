// src/hooks/useProfileData.ts
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { profileService, ProfileData } from '../services/profileService';

export const useProfileData = (username: string | undefined) => {
    const { user } = useAuth();
    const [profileData, setProfileData] = useState<ProfileData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [isOwnProfile, setIsOwnProfile] = useState<boolean>(false);

    const fetchProfileData = useCallback(async () => {
        if (!username) return;

        try {
            setLoading(true);

            // Używamy profileService zamiast bezpośredniego fetcha
            const data = await profileService.getUserProfile(username);
            setProfileData(data);

            setIsOwnProfile(user ? user.username === username : false);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [username, user]);

    useEffect(() => {
        fetchProfileData();
    }, [fetchProfileData]);

    return {
        profileData,
        loading,
        error,
        isOwnProfile,
        refreshProfile: fetchProfileData
    };
};

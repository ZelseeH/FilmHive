
import { useState, useRef, useEffect } from 'react';
import { profileService } from '../services/profileService';

export const useProfilePicture = (onImageUpdate?: () => void) => {
    const [showProfilePicMenu, setShowProfilePicMenu] = useState(false);
    const [uploadingProfilePic, setUploadingProfilePic] = useState(false);

    const profilePicMenuRef = useRef<HTMLDivElement>(null);
    const profilePicInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (profilePicMenuRef.current && !profilePicMenuRef.current.contains(event.target as Node)) {
                setShowProfilePicMenu(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const handleProfilePicClick = () => {
        setShowProfilePicMenu(!showProfilePicMenu);
    };

    const handleProfilePicChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files || e.target.files.length === 0) return;

        const file = e.target.files[0];
        setUploadingProfilePic(true);
        setShowProfilePicMenu(false);

        try {
            await profileService.uploadProfilePicture(file);
            onImageUpdate?.();
        } catch (error) {
            console.error('Błąd podczas przesyłania zdjęcia profilowego:', error);
        } finally {
            setUploadingProfilePic(false);
        }
    };

    return {
        showProfilePicMenu,
        uploadingProfilePic,
        profilePicInputRef,
        profilePicMenuRef,
        handleProfilePicClick,
        handleProfilePicChange
    };
};
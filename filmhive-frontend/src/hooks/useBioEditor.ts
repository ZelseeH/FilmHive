
// hooks/useBioEditor.ts
import { useState } from 'react';
import { profileService } from '../services/profileService';

export const useBioEditor = (initialBio: string = '', onBioUpdate?: () => void) => {
    const [bio, setBio] = useState(initialBio);
    const [isEditingBio, setIsEditingBio] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleBioClick = () => {
        setIsEditingBio(true);
    };

    const handleBioChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setBio(e.target.value);
    };

    const handleBioSave = async (token: string) => {
        setLoading(true);
        try {
            if (!token) throw new Error('Brak tokenu autoryzacyjnego');

            await profileService.updateBio(bio, token);
            setIsEditingBio(false);
            onBioUpdate?.();
        } catch (error) {
            console.error('Błąd podczas aktualizacji opisu:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleBioCancel = () => {
        setIsEditingBio(false);
    };

    return {
        bio,
        setBio,
        isEditingBio,
        loading,
        handleBioClick,
        handleBioChange,
        handleBioSave,
        handleBioCancel
    };
};
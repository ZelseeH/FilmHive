
// components/ProfileHeader/BioEditor.tsx
import React from 'react';
import styles from '../ProfileHeader/ProfileHeader.module.css';

interface BioEditorProps {
    bio: string;
    isEditingBio: boolean;
    isOwnProfile: boolean;
    loading: boolean;
    onBioClick: () => void;
    onBioChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    onBioSave: () => void;
    onBioCancel: () => void;
}

export const BioEditor: React.FC<BioEditorProps> = ({
    bio,
    isEditingBio,
    isOwnProfile,
    loading,
    onBioClick,
    onBioChange,
    onBioSave,
    onBioCancel
}) => {
    return (
        <div
            className={`${styles['profile-bio']} ${isOwnProfile ? styles.editable : ''}`}
            onClick={!isEditingBio && isOwnProfile ? onBioClick : undefined}
        >
            {isEditingBio ? (
                <>
                    <textarea
                        value={bio}
                        onChange={onBioChange}
                        placeholder="Kliknij, aby powiedzieć innym coś o sobie"
                        maxLength={500}
                    />
                    <div className={styles['bio-actions']}>
                        <button
                            onClick={onBioCancel}
                            className={styles['cancel-btn']}
                        >
                            Anuluj
                        </button>
                        <button
                            onClick={onBioSave}
                            disabled={loading}
                            className={styles['save-btn']}
                        >
                            {loading ? 'Zapisywanie...' : 'Zapisz'}
                        </button>
                    </div>
                </>
            ) : (
                <p>
                    {bio || (
                        isOwnProfile
                            ? 'Kliknij, aby powiedzieć innym coś o sobie'
                            : 'Użytkownik nie dodał jeszcze opisu.'
                    )}
                </p>
            )}
        </div>
    );
};
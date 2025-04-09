// components/ProfileHeader/ProfilePicture.tsx
import React from 'react';
import { getInitial } from '../../utils/profileUtils';
import styles from '../ProfileHeader/ProfileHeader.module.css';

interface ProfilePictureProps {
    profileData?: {
        username?: string;
        profile_picture?: string;
    };
    isOwnProfile: boolean;
    showMenu: boolean;
    uploadingProfilePic: boolean;
    profilePicMenuRef: React.RefObject<HTMLDivElement | null>;
    profilePicInputRef: React.RefObject<HTMLInputElement | null>;
    onProfilePicClick: () => void;
    onProfilePicChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export const ProfilePicture: React.FC<ProfilePictureProps> = ({
    profileData,
    isOwnProfile,
    showMenu,
    uploadingProfilePic,
    profilePicMenuRef,
    profilePicInputRef,
    onProfilePicClick,
    onProfilePicChange
}) => {
    return (
        <div className={styles['profile-picture-container']}>
            <div
                className={`${styles['profile-picture']} ${isOwnProfile ? styles.editable : ''}`}
                onClick={isOwnProfile ? onProfilePicClick : undefined}
            >
                {profileData?.profile_picture ? (
                    <img
                        src={profileData.profile_picture}
                        alt={`Profil ${profileData.username}`}
                    />
                ) : (
                    <div className={styles['profile-initial']}>
                        {getInitial(profileData?.username)}
                    </div>
                )}
            </div>

            {isOwnProfile && showMenu && (
                <div ref={profilePicMenuRef} className={styles['profile-pic-menu']}>
                    <label className={styles['menu-item']}>
                        {uploadingProfilePic ? 'Przesyłanie...' : 'Zmień zdjęcie'}
                        <input
                            type="file"
                            ref={profilePicInputRef}
                            onChange={onProfilePicChange}
                            accept="image/png, image/jpeg, image/jpg"
                            style={{ display: 'none' }}
                            disabled={uploadingProfilePic}
                        />
                    </label>
                </div>
            )}
        </div>
    );
};

// components/ProfileHeader/ProfileHeader.tsx
import React, { useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { BackgroundImage } from './BackgroundImage';
import { ProfilePicture } from './ProfilePicture';
import { BioEditor } from './BioEditor';
import { useBackgroundImage } from '../../hooks/useBackgroundImage';
import { useProfilePicture } from '../../hooks/useProfilePicture';
import { useBioEditor } from '../../hooks/useBioEditor';
import styles from './ProfileHeader.module.css';

interface UserProfile {
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

interface ProfileHeaderProps {
  profileData?: UserProfile;
  isOwnProfile: boolean;
  onBioUpdate?: () => void;
  onImageUpdate?: () => void;
}

const ProfileHeader: React.FC<ProfileHeaderProps> = ({
  profileData,
  isOwnProfile,
  onBioUpdate,
  onImageUpdate
}) => {
  const { getToken } = useAuth();

  const {
    bio,
    setBio,
    isEditingBio,
    loading: bioLoading,
    handleBioClick,
    handleBioChange,
    handleBioSave,
    handleBioCancel
  } = useBioEditor(profileData?.bio || '', onBioUpdate);

  const {
    showProfilePicMenu,
    uploadingProfilePic,
    profilePicInputRef,
    profilePicMenuRef,
    handleProfilePicClick,
    handleProfilePicChange
  } = useProfilePicture(onImageUpdate);

  const {
    tempBackgroundImage,
    backgroundPosition,
    isDragging,
    uploadingBgImage,
    backgroundRef,
    backgroundImageInputRef,
    handleBackgroundClick,
    handleBackgroundChange,
    handleBackgroundMouseDown,
    handleSaveBackground,
    handleCancelBackground
  } = useBackgroundImage(onImageUpdate);

  // Aktualizuj bio, gdy zmienia się profileData
  useEffect(() => {
    setBio(profileData?.bio || '');
  }, [profileData, setBio]);

  const handleSaveBio = () => {
    const token = getToken();
    if (token) {
      handleBioSave(token);
    }
  };

  return (
    <div className={styles['profile-header']}>
      <BackgroundImage
        backgroundRef={backgroundRef}
        tempBackgroundImage={tempBackgroundImage}
        profileData={profileData}
        backgroundPosition={backgroundPosition}
        isOwnProfile={isOwnProfile}
        isDragging={isDragging}
        uploadingBgImage={uploadingBgImage}
        onBackgroundClick={handleBackgroundClick}
        onMouseDown={handleBackgroundMouseDown}
        backgroundImageInputRef={backgroundImageInputRef}
        onBackgroundChange={handleBackgroundChange}
        onSaveBackground={handleSaveBackground}
        onCancelBackground={handleCancelBackground}
      />

      <div className={styles['profile-header-top']}>
        <ProfilePicture
          profileData={profileData}
          isOwnProfile={isOwnProfile}
          showMenu={showProfilePicMenu}
          uploadingProfilePic={uploadingProfilePic}
          profilePicMenuRef={profilePicMenuRef}
          profilePicInputRef={profilePicInputRef}
          onProfilePicClick={handleProfilePicClick}
          onProfilePicChange={handleProfilePicChange}
        />

        <div className={styles['profile-info']}>
          <h1>{profileData?.name || profileData?.username || 'Użytkownik'}</h1>
          {profileData?.username && <h2>@{profileData.username}</h2>}
        </div>
      </div>

      <BioEditor
        bio={bio}
        isEditingBio={isEditingBio}
        isOwnProfile={isOwnProfile}
        loading={bioLoading}
        onBioClick={handleBioClick}
        onBioChange={handleBioChange}
        onBioSave={handleSaveBio}
        onBioCancel={handleBioCancel}
      />

      <div className={styles['profile-footer']}>
        <p>
          Na FilmHive od {profileData?.registration_date
            ? new Date(profileData.registration_date).toLocaleDateString('pl-PL')
            : '31 lipca 2020'}
        </p>
      </div>
    </div>
  );
};

export default ProfileHeader;

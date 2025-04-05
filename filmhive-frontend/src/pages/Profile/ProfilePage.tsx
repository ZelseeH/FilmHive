// src/pages/Profile/ProfilePage.tsx
import React from 'react';
import { useParams } from 'react-router-dom';
import ProfileHeader from '../../components/ProfileHeader/ProfileHeader';
import { useProfileData } from '../../hooks/useProfileData';
import styles from './ProfilePage.module.css';

const ProfilePage: React.FC = () => {
  const { username } = useParams<{ username?: string }>();
  const { profileData, loading, error, isOwnProfile, refreshProfile } = useProfileData(username);

  if (loading) {
    return <div className={`${styles['profile-page']} ${styles.loading}`}>Ładowanie profilu...</div>;
  }

  if (error) {
    return <div className={`${styles['profile-page']} ${styles.error}`}>Błąd: {error}</div>;
  }

  if (!profileData) {
    return <div className={`${styles['profile-page']} ${styles.error}`}>Nie znaleziono profilu</div>;
  }

  return (
    <div className={styles['profile-page']}>
      <ProfileHeader
        profileData={profileData}
        isOwnProfile={isOwnProfile}
        onBioUpdate={refreshProfile}
        onImageUpdate={refreshProfile}
      />

      <div className={styles['profile-content']}>
        <div className={styles['profile-section']}>
          <h2>Aktywność</h2>
          <p>Tutaj będzie wyświetlana aktywność użytkownika</p>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;

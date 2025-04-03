// src/pages/Profile/ProfilePage.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import ProfileHeader from '../../components/ProfileHeader/ProfileHeader';
import styles from './ProfilePage.module.css';

interface ProfileData {
  username: string;
  bio?: string;
  // Dodaj inne pola, które są w twoim profileData
}

interface ProfileHeaderProps {
  profileData: ProfileData;
  isOwnProfile: boolean;
  onBioUpdate: () => void;
}

const ProfilePage: React.FC = () => {
  const { username } = useParams<{ username?: string }>();
  const { user } = useAuth();
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isOwnProfile, setIsOwnProfile] = useState<boolean>(false);

  const fetchProfileData = useCallback(async () => {
    if (!username) return;

    try {
      setLoading(true);

      const response = await fetch(`http://localhost:5000/api/user/profile/${username}`);

      if (!response.ok) {
        throw new Error('Nie udało się pobrać danych profilu');
      }

      const data = await response.json();
      setProfileData(data);

      // Naprawiony błąd: użycie operatora warunkowego zamiast &&
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
        onBioUpdate={fetchProfileData}
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

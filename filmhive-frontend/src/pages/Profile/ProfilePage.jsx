import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import ProfileHeader from '../../components/ProfileHeader/ProfileHeader';
import styles from './ProfilePage.module.css';

const ProfilePage = () => {
  const { username } = useParams();
  const { user } = useAuth();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOwnProfile, setIsOwnProfile] = useState(false);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`http://localhost:5000/api/user/profile/${username}`);
      
      if (!response.ok) {
        throw new Error('Nie udało się pobrać danych profilu');
      }
      
      const data = await response.json();
      setProfileData(data);
      
      setIsOwnProfile(user && user.username === username);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (username) {
      fetchProfileData();
    }
  }, [username, user]);

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
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext.tsx';
import styles from './ProfileHeader.module.css';

const ProfileHeader = ({ profileData, isOwnProfile, onBioUpdate }) => {
  const [bio, setBio] = useState(profileData?.bio || '');
  const [isEditingBio, setIsEditingBio] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setBio(profileData?.bio || '');
  }, [profileData]);

  const handleBioClick = () => {
    if (isOwnProfile) {
      setIsEditingBio(true);
    }
  };

  const handleBioChange = (e) => {
    setBio(e.target.value);
  };

  const handleBioSave = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/user/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ bio })
      });

      if (response.ok) {
        setIsEditingBio(false);
        if (onBioUpdate) {
          onBioUpdate();
        }
      } else {
        const errorData = await response.json();
        console.error('Error updating bio:', errorData.error);
      }
    } catch (error) {
      console.error('Error updating bio:', error);
    } finally {
      setLoading(false);
    }
  };

  const getInitial = () => {
    return profileData?.username ? profileData.username[0].toUpperCase() : '?';
  };

  return (
    <div className={styles['profile-header']}>
      <div className={styles['profile-header-top']}>
        <div className={styles['profile-picture']}>
          {profileData?.profile_picture ? (
            <img src={profileData.profile_picture} alt="Profile" />
          ) : (
            <div className={styles['profile-initial']}>{getInitial()}</div>
          )}
        </div>
        <div className={styles['profile-info']}>
          <h1>{profileData?.name || profileData?.username || 'Użytkownik'}</h1>
          <h2>{profileData?.username || ''}</h2>
        </div>
      </div>

      <div
        className={`${styles['profile-bio']} ${isOwnProfile ? styles.editable : ''}`}
        onClick={!isEditingBio && isOwnProfile ? handleBioClick : undefined}
      >
        {isEditingBio ? (
          <>
            <textarea
              value={bio}
              onChange={handleBioChange}
              placeholder="Kliknij, aby powiedzieć innym coś o sobie"
            />
            <div className={styles['bio-actions']}>
              <button onClick={() => setIsEditingBio(false)} className={styles['cancel-btn']}>
                Anuluj
              </button>
              <button onClick={handleBioSave} disabled={loading} className={styles['save-btn']}>
                {loading ? 'Zapisywanie...' : 'Zapisz'}
              </button>
            </div>
          </>
        ) : (
          <p>{profileData?.bio || (isOwnProfile ? 'Kliknij, aby powiedzieć innym coś o sobie' : 'Użytkownik nie dodał jeszcze opisu.')}</p>
        )}
      </div>

      <div className={styles['profile-footer']}>
        <p>Na FilmHive od {profileData?.registration_date ? new Date(profileData.registration_date).toLocaleDateString('pl-PL') : '31 lipca 2020'}</p>
      </div>
    </div>
  );
};

export default ProfileHeader;
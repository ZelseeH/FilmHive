import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { profileService } from '../../services/profileService';
import { getInitial } from '../../utils/profileUtils';
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
  const [bio, setBio] = useState(profileData?.bio || '');
  const [isEditingBio, setIsEditingBio] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploadingProfilePic, setUploadingProfilePic] = useState(false);
  const [uploadingBgImage, setUploadingBgImage] = useState(false);
  const [showProfilePicMenu, setShowProfilePicMenu] = useState(false);
  const [tempBackgroundImage, setTempBackgroundImage] = useState<string | null>(null);
  const [backgroundPosition, setBackgroundPosition] = useState({ x: 50, y: 50 });
  const [isDragging, setIsDragging] = useState(false);

  const profilePicInputRef = useRef<HTMLInputElement>(null);
  const backgroundImageInputRef = useRef<HTMLInputElement>(null);
  const profilePicMenuRef = useRef<HTMLDivElement>(null);
  const backgroundRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setBio(profileData?.bio || '');
  }, [profileData]);

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

  // Efekt do obsługi przeciągania tła
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging && tempBackgroundImage && backgroundRef.current) {
        const rect = backgroundRef.current.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        // Ograniczenie wartości x i y do zakresu 0-100
        const clampedX = Math.max(0, Math.min(100, x));
        const clampedY = Math.max(0, Math.min(100, y));

        setBackgroundPosition({ x: clampedX, y: clampedY });
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, tempBackgroundImage]);

  const handleBioClick = () => {
    if (isOwnProfile) setIsEditingBio(true);
  };

  const handleBioChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setBio(e.target.value);
  };

  const handleBioSave = async () => {
    setLoading(true);
    try {
      const token = getToken();
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

  const handleProfilePicClick = () => {
    if (isOwnProfile) {
      setShowProfilePicMenu(!showProfilePicMenu);
    }
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

  const handleBackgroundClick = () => {
    if (isOwnProfile && !uploadingBgImage && !tempBackgroundImage) {
      backgroundImageInputRef.current?.click();
    }
  };

  const handleBackgroundChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const file = e.target.files[0];
    const reader = new FileReader();

    reader.onload = (event) => {
      if (event.target && typeof event.target.result === 'string') {
        setTempBackgroundImage(event.target.result);
        // Resetuj pozycję na środek przy nowym zdjęciu
        setBackgroundPosition({ x: 50, y: 50 });
      }
    };

    reader.readAsDataURL(file);
  };

  const handleBackgroundMouseDown = (e: React.MouseEvent) => {
    if (tempBackgroundImage) {
      setIsDragging(true);
    }
  };

  const handleSaveBackground = async () => {
    if (!tempBackgroundImage) return;

    setUploadingBgImage(true);
    try {
      // Konwertuj base64 na plik
      const response = await fetch(tempBackgroundImage);
      const blob = await response.blob();
      const file = new File([blob], 'background.jpg', { type: 'image/jpeg' });

      // Przekaż pozycję tła do serwisu
      await profileService.uploadBackgroundImage(file, backgroundPosition);
      onImageUpdate?.();
    } catch (error) {
      console.error('Błąd podczas przesyłania zdjęcia w tle:', error);
    } finally {
      setUploadingBgImage(false);
      setTempBackgroundImage(null);
      setIsDragging(false);
    }
  };


  return (
    <div className={styles['profile-header']}>
      <div
        ref={backgroundRef}
        className={`${styles['profile-background']} ${isOwnProfile ? styles.editable : ''} ${tempBackgroundImage ? styles.draggable : ''}`}
        style={{
          backgroundImage: tempBackgroundImage
            ? `url(${tempBackgroundImage})`
            : profileData?.background_image
              ? `url(${profileData.background_image})`
              : 'none',
          backgroundPosition: tempBackgroundImage
            ? `${backgroundPosition.x}% ${backgroundPosition.y}%`
            : profileData?.background_position
              ? `${profileData.background_position.x}% ${profileData.background_position.y}%`
              : '50% 50%'
        }}
        onClick={isOwnProfile && !tempBackgroundImage ? handleBackgroundClick : undefined}
        onMouseDown={isOwnProfile && tempBackgroundImage ? handleBackgroundMouseDown : undefined}
      >
        {isOwnProfile && (
          <>
            <input
              type="file"
              ref={backgroundImageInputRef}
              onChange={handleBackgroundChange}
              accept="image/png, image/jpeg, image/jpg"
              style={{ display: 'none' }}
            />
            {tempBackgroundImage ? (
              <div className={styles['background-actions']}>
                <div className={styles['background-instructions']}>
                  Przeciągnij, aby dostosować pozycję zdjęcia
                </div>
                <div>
                  <button onClick={handleSaveBackground} disabled={uploadingBgImage}>
                    {uploadingBgImage ? 'Zapisywanie...' : 'Zapisz zdjęcie'}
                  </button>
                  <button onClick={() => setTempBackgroundImage(null)}>Anuluj</button>
                </div>
              </div>
            ) : (
              <div className={styles['edit-overlay']}>
                {uploadingBgImage ? 'Przesyłanie...' : 'Zmień zdjęcie w tle'}
              </div>
            )}
          </>
        )}
      </div>

      <div className={styles['profile-header-top']}>
        <div className={styles['profile-picture-container']}>
          <div
            className={`${styles['profile-picture']} ${isOwnProfile ? styles.editable : ''}`}
            onClick={handleProfilePicClick}
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

          {isOwnProfile && showProfilePicMenu && (
            <div ref={profilePicMenuRef} className={styles['profile-pic-menu']}>
              <label className={styles['menu-item']}>
                Zmień zdjęcie
                <input
                  type="file"
                  ref={profilePicInputRef}
                  onChange={handleProfilePicChange}
                  accept="image/png, image/jpeg, image/jpg"
                  style={{ display: 'none' }}
                />
              </label>
            </div>
          )}
        </div>

        <div className={styles['profile-info']}>
          <h1>{profileData?.name || profileData?.username || 'Użytkownik'}</h1>
          {profileData?.username && <h2>@{profileData.username}</h2>}
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
              maxLength={500}
            />
            <div className={styles['bio-actions']}>
              <button
                onClick={() => setIsEditingBio(false)}
                className={styles['cancel-btn']}
              >
                Anuluj
              </button>
              <button
                onClick={handleBioSave}
                disabled={loading}
                className={styles['save-btn']}
              >
                {loading ? 'Zapisywanie...' : 'Zapisz'}
              </button>
            </div>
          </>
        ) : (
          <p>
            {profileData?.bio || (
              isOwnProfile
                ? 'Kliknij, aby powiedzieć innym coś o sobie'
                : 'Użytkownik nie dodał jeszcze opisu.'
            )}
          </p>
        )}
      </div>

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


// components/ProfileHeader/BackgroundImage.tsx
import React from 'react';
import styles from './ProfileHeader.module.css';

interface BackgroundImageProps {
    backgroundRef: React.RefObject<HTMLDivElement | null>;
    tempBackgroundImage: string | null;
    profileData?: {
        background_image?: string;
        background_position?: { x: number; y: number };
    };
    backgroundPosition: { x: number; y: number };
    isOwnProfile: boolean;
    isDragging: boolean;
    uploadingBgImage: boolean;
    onBackgroundClick?: () => void;
    onMouseDown?: (e: React.MouseEvent) => void;
    backgroundImageInputRef: React.RefObject<HTMLInputElement | null>;
    onBackgroundChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onSaveBackground: () => void;
    onCancelBackground: () => void;
}

export const BackgroundImage: React.FC<BackgroundImageProps> = ({
    backgroundRef,
    tempBackgroundImage,
    profileData,
    backgroundPosition,
    isOwnProfile,
    isDragging,
    uploadingBgImage,
    onBackgroundClick,
    onMouseDown,
    backgroundImageInputRef,
    onBackgroundChange,
    onSaveBackground,
    onCancelBackground
}) => {
    return (
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
                        : '50% 50%',
                backgroundSize: 'cover',
                backgroundRepeat: 'no-repeat',
                cursor: tempBackgroundImage && isOwnProfile ? (isDragging ? 'grabbing' : 'grab') : 'default'
            }}
            onClick={isOwnProfile && !tempBackgroundImage ? onBackgroundClick : undefined}
            onMouseDown={isOwnProfile && tempBackgroundImage ? onMouseDown : undefined}
        >
            {isOwnProfile && (
                <>
                    <input
                        type="file"
                        ref={backgroundImageInputRef}
                        onChange={onBackgroundChange}
                        accept="image/png, image/jpeg, image/jpg"
                        style={{ display: 'none' }}
                    />
                    {tempBackgroundImage ? (
                        <div className={styles['background-actions']}>
                            <div className={styles['background-instructions']}>
                                Przeciągnij, aby dostosować pozycję zdjęcia
                            </div>
                            <div>
                                <button onClick={onSaveBackground} disabled={uploadingBgImage}>
                                    {uploadingBgImage ? 'Zapisywanie...' : 'Zapisz zdjęcie'}
                                </button>
                                <button onClick={onCancelBackground}>
                                    Anuluj
                                </button>
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
    );
};
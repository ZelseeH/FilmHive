// src/components/Navbar/UserAvatar/UserAvatar.tsx
import React from 'react';
import styles from './UserAvatar.module.css';

interface User {
    username?: string;
    profile_picture?: string;
}

interface UserAvatarProps {
    user: User;
    onClick: (e: React.MouseEvent) => void;
    className?: string;
}

const UserAvatar: React.FC<UserAvatarProps> = ({ user, onClick, className }) => {
    return (
        <div className={`${styles['user-avatar']} ${className || ''}`} onClick={onClick}>
            {user.profile_picture ? (
                <img src={user.profile_picture} alt={user.username || 'Użytkownik'} />
            ) : (
                <div className={styles['user-initial']}>
                    {user.username ? user.username[0].toUpperCase() : '?'}
                </div>
            )}
        </div>
    );
};

export default UserAvatar;

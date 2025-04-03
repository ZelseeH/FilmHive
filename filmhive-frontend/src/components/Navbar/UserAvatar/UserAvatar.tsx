// src/components/Navbar/UserAvatar/UserAvatar.tsx
import React from 'react';
import styles from './UserAvatar.module.css';

interface User {
    username?: string;
    avatar?: string;
}

interface UserAvatarProps {
    user: User;
    onClick: () => void;
}

const UserAvatar: React.FC<UserAvatarProps> = ({ user, onClick }) => {
    return (
        <div className={styles['user-avatar']} onClick={onClick}>
            {user.avatar ? (
                <img src={user.avatar} alt={user.username} />
            ) : (
                <div className={styles['user-initial']}>{user.username?.[0].toUpperCase()}</div>
            )}
        </div>
    );
};

export default UserAvatar;

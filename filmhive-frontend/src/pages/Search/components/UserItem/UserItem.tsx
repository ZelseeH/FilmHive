import React from 'react';
import { Link } from 'react-router-dom';
import styles from './UserItem.module.css';

export interface User {
    id: number;
    username: string;
    name?: string;
    profile_picture?: string;
    registration_date?: string;
}

interface UserItemProps {
    user: User;
}

const UserItem: React.FC<UserItemProps> = ({ user }) => {
    return (
        <div className={styles.userItem}>
            <div className={styles.userAvatar}>
                <Link to={`/profile/${user.username}`}>
                    <img
                        src={user.profile_picture || '/default-avatar.png'}
                        alt={user.username}
                        onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = '/default-avatar.png';
                            target.onerror = null;
                        }}
                    />
                </Link>
            </div>
            <div className={styles.userInfo}>
                <div className={styles.userLabel}>UŻYTKOWNIK</div>
                <div className={styles.userHeader}>
                    <h3 className={styles.userName}>
                        <Link to={`/profile/${user.username}`}>{user.username}</Link>
                    </h3>
                    {user.name && (
                        <p className={styles.userFullName}>{user.name}</p>
                    )}
                </div>
                {user.registration_date && (
                    <div className={styles.userRegistration}>
                        Dołączył: {new Date(user.registration_date).toLocaleDateString()}
                    </div>
                )}
            </div>
        </div>
    );
};

export default UserItem;

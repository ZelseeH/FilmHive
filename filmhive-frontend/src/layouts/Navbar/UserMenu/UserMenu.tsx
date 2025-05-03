import React from 'react';
import { Link } from 'react-router-dom';
import styles from './UserMenu.module.css';

interface UserMenuProps {
    username: string;
    onClose: () => void;
    onLogout: () => void;
    position: { top: number; left: number };
    role?: number;
}

const UserMenu: React.FC<UserMenuProps> = ({ username, onClose, onLogout, position, role }) => {
    const handleLogout = () => {
        onLogout();
        window.location.reload();
    };

    return (
        <div
            className={styles['user-menu']}
            style={{
                top: `${position.top}px`,
                left: `${position.left}px`,
                transform: 'translateX(-50%)'
            }}
        >
            <Link
                to={`/profile/${username}`}
                className={styles['user-menu-item']}
                onClick={onClose}
            >
                Mój Profil
            </Link>
            <Link
                to="/settings"
                className={styles['user-menu-item']}
                onClick={onClose}
            >
                Ustawienia
            </Link>
            {/* Panel Administratora - tylko dla roli 1 (admin) */}
            {role === 1 && (
                <Link
                    to="/dashboard"
                    className={styles['user-menu-item']}
                    onClick={onClose}
                >
                    Panel Administratora
                </Link>
            )}
            {/* Panel Moderatora - tylko dla roli 2 (moderator) */}
            {role === 2 && (
                <Link
                    to="/dashboard"
                    className={styles['user-menu-item']}
                    onClick={onClose}
                >
                    Panel Moderatora
                </Link>
            )}
            <button
                className={`${styles['user-menu-item']} ${styles['logout-btn']}`}
                onClick={handleLogout}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    fill="currentColor"
                    viewBox="0 0 16 16"
                    className={styles['logout-icon']}
                >
                    <path
                        fillRule="evenodd"
                        d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"
                    />
                    <path
                        fillRule="evenodd"
                        d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"
                    />
                </svg>
                <span className={styles['logout-text']}>Wyloguj</span>
            </button>
        </div>
    );
};

export default UserMenu;
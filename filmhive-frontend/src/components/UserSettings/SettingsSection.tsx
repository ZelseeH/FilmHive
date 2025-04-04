import React from 'react';
import styles from './UserSettings.module.css';

// Define the interfaces needed
interface UserData {
    username: string;
    name: string;
    bio: string;
    email: string;
}

interface EditModeState {
    username: boolean;
    bio: boolean;
    email: boolean;
    password: boolean;
    name: boolean;
}

interface SettingsSectionProps {
    userData: UserData;
    handleEdit: (field: keyof EditModeState) => void;
}

const SettingsSection: React.FC<SettingsSectionProps> = ({ userData, handleEdit }) => {
    return (
        <div className={styles['settings-section']}>
            <div className={styles['setting-item']}>
                <div className={styles['setting-label']}>Nazwa Użytkownika</div>
                <div className={styles['setting-value']}>
                    {userData.name || 'Nie podano'}
                    <button className={styles['edit-button']} onClick={() => handleEdit('name')}>✏️</button>
                </div>
            </div>

            <div className={styles['setting-item']}>
                <div className={styles['setting-label']}>Login</div>
                <div className={styles['setting-value']}>
                    {userData.username}
                </div>
            </div>

            <div className={styles['setting-item']}>
                <div className={styles['setting-label']}>E-mail</div>
                <div className={styles['setting-value']}>
                    {userData.email}
                    <button className={styles['edit-button']} onClick={() => handleEdit('email')}>✏️</button>
                </div>
            </div>

            <div className={styles['setting-item']}>
                <div className={styles['setting-label']}>Hasło</div>
                <div className={styles['setting-value']}>
                    ••••••
                    <button className={styles['edit-button']} onClick={() => handleEdit('password')}>✏️</button>
                </div>
            </div>
        </div>
    );
};

export default SettingsSection;

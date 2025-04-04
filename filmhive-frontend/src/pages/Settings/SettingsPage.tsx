import React from 'react';
import styles from './SettingsPage.module.css';
import UserSettings from '../../components/UserSettings/UserSettings';

const SettingsPage: React.FC = () => {
  return (
    <div className={styles.settingsPage}>
      <h1>Ustawienia użytkownika</h1>
      <UserSettings />
    </div>
  );
};

export default SettingsPage;

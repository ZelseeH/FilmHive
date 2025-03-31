import React from 'react';
import './SettingsPage.css';
import UserSettings from '../../components/UserSettings/UserSettings';

const SettingsPage = () => {
  return (
    <div className="settings-page">
      <h1>Ustawienia użytkownika</h1>
      <UserSettings />
    </div>
  );
};

export default SettingsPage;

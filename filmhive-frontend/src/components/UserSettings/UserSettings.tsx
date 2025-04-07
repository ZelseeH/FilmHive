import React from 'react';
import { useUserSettings } from '../../hooks/useUserSettings';
import { userService } from '../../services/userService';
import { authUtils } from '../../utils/authUtils';
import SettingsSection from './SettingsSection';
import EditModal from './EditModal';
import styles from './UserSettings.module.css';

const UserSettings: React.FC = () => {
  const {
    userData,
    editMode,
    formValues,
    message,
    modalErrors,
    loading,
    handleEdit,
    handleCancel,
    handleChange,
    setModalErrors,
    setMessage,
    setUserData,
    setLoading
  } = useUserSettings();

  const handleUpdateName = async () => {
    setModalErrors(prev => ({ ...prev, name: '' }));
    setLoading(true);
    try {
      const data = await userService.updateProfile({ name: formValues.name });
      setUserData(prev => ({ ...prev, name: data.name }));
      setMessage({ type: 'success', text: 'Nazwa uĹźytkownika zostaĹa zmieniona.' });
      handleCancel();
    } catch (error: unknown) {
      if (error instanceof Error) {
        const errorMessage: string = error.message;
        setModalErrors(prev => ({ ...prev, name: errorMessage || 'Wystąpił błąd podczas aktualizacji imienia i nazwiska.' }));
      } else {
        setModalErrors(prev => ({ ...prev, name: 'Wystąpił nieznany błąd podczas aktualizacji imienia i nazwiska.' }));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateBio = async () => {
    setModalErrors(prev => ({ ...prev, bio: '' }));
    setLoading(true);
    try {
      const data = await userService.updateProfile({ bio: formValues.bio });
      setUserData(prev => ({ ...prev, bio: data.bio }));
      setMessage({ type: 'success', text: 'Opis Został zmieniony.' });
      handleCancel();
    } catch (error: unknown) {
      if (error instanceof Error) {
        const errorMessage: string = error.message;
        setModalErrors(prev => ({ ...prev, bio: errorMessage || 'Wystąpił błąd podczas aktualizacji opisu.' }));
      } else {
        setModalErrors(prev => ({ ...prev, bio: 'Wystąpił nieznany błąd podczas aktualizacji opisu.' }));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateEmail = async () => {
    setModalErrors(prev => ({ ...prev, email: '' }));

    if (!formValues.currentPassword) {
      setModalErrors(prev => ({ ...prev, email: 'Podaj aktualne hasło, aby zmienić email.' }));
      return;
    }

    setLoading(true);
    try {
      const data = await userService.updateEmail(formValues.email, formValues.currentPassword);
      setUserData(prev => ({ ...prev, email: data.email }));
      setMessage({ type: 'success', text: 'Adres email został zmieniony.' });
      handleCancel();
    } catch (error: unknown) {
      if (error instanceof Error) {
        const errorMessage: string = error.message;
        setModalErrors(prev => ({ ...prev, email: errorMessage || 'Wystąpił błąd podczas aktualizacji adresu email.' }));
      } else {
        setModalErrors(prev => ({ ...prev, email: 'Wystąpił nieznany błąd podczas aktualizacji adresu email.' }));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePassword = async () => {
    setModalErrors(prev => ({ ...prev, password: '' }));

    const passwordValidation = authUtils.validatePassword(formValues.newPassword, formValues.confirmPassword);
    if (!passwordValidation.valid) {
      setModalErrors(prev => ({ ...prev, password: passwordValidation.error }));
      return;
    }

    if (!formValues.currentPassword) {
      setModalErrors(prev => ({ ...prev, password: 'Podaj aktualne Hasło.' }));
      return;
    }

    setLoading(true);
    try {
      await userService.changePassword(formValues.currentPassword, formValues.newPassword);
      setMessage({ type: 'success', text: 'Hasło Zostało zmienione.' });
      handleCancel();
    } catch (error: unknown) {
      if (error instanceof Error) {
        const errorMessage: string = error.message;
        setModalErrors(prev => ({ ...prev, password: errorMessage || 'Wystąpił błąd podczas zmiany hasła.' }));
      } else {
        setModalErrors(prev => ({ ...prev, password: 'Wystąpił nieznany błąd podczas zmiany hasła.' }));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles['page-container']}>
      <div className={styles['user-settings-container']}>
        <div className={styles['settings-divider']}></div>

        {message.text && (
          <div className={`${styles.message} ${styles[message.type]}`}>
            {message.text}
          </div>
        )}

        <h2 className={styles['settings-section-title']}>Dane logowania</h2>
        <SettingsSection
          userData={userData}
          handleEdit={handleEdit}
        />

        <div className={styles['settings-divider']}></div>

        {editMode && 'name' in editMode && editMode.name && (
          <EditModal
            title="Zmień nazwę użytkownika"
            error={modalErrors && 'name' in modalErrors ? modalErrors.name : ''}
            loading={loading}
            onCancel={handleCancel}
            onSave={handleUpdateName}
          >
            <div className={styles['form-group']}>
              <label>Nazwa Użytkownika</label>
              <input
                type="text"
                name="name"
                value={formValues.name}
                onChange={handleChange}
              />
            </div>
          </EditModal>
        )}

        {editMode && 'bio' in editMode && editMode.bio && (
          <EditModal
            title="Zmień opis"
            error={modalErrors && 'bio' in modalErrors ? modalErrors.bio : ''}
            loading={loading}
            onCancel={handleCancel}
            onSave={handleUpdateBio}
          >
            <div className={styles['form-group']}>
              <label>O mnie</label>
              <textarea
                name="bio"
                value={formValues.bio}
                onChange={handleChange}
                rows={4}
              />
            </div>
          </EditModal>
        )}

        {editMode && 'email' in editMode && editMode.email && (
          <EditModal
            title="Zmień adres email"
            error={modalErrors && 'email' in modalErrors ? modalErrors.email : ''}
            loading={loading}
            onCancel={handleCancel}
            onSave={handleUpdateEmail}
          >
            <div className={styles['form-group']}>
              <label>Nowy adres email</label>
              <input
                type="email"
                name="email"
                value={formValues.email}
                onChange={handleChange}
              />
            </div>
            <div className={styles['form-group']}>
              <label>Aktualne Hasło</label>
              <input
                type="password"
                name="currentPassword"
                value={formValues.currentPassword}
                onChange={handleChange}
              />
            </div>
          </EditModal>
        )}

        {editMode && 'password' in editMode && editMode.password && (
          <EditModal
            title="Zmień Hasło"
            error={modalErrors && 'password' in modalErrors ? modalErrors.password : ''}
            loading={loading}
            onCancel={handleCancel}
            onSave={handleUpdatePassword}
          >
            <div className={styles['form-group']}>
              <label>Aktualne Hasło</label>
              <input
                type="password"
                name="currentPassword"
                value={formValues.currentPassword}
                onChange={handleChange}
              />
            </div>
            <div className={styles['form-group']}>
              <label>Nowe Hasłó</label>
              <input
                type="password"
                name="newPassword"
                value={formValues.newPassword}
                onChange={handleChange}
              />
            </div>
            <div className={styles['form-group']}>
              <label>Powtórz Nowe Hasło</label>
              <input
                type="password"
                name="confirmPassword"
                value={formValues.confirmPassword}
                onChange={handleChange}
              />
            </div>
          </EditModal>
        )}
      </div>
    </div>
  );
};

export default UserSettings;
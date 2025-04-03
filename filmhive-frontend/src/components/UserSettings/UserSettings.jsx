import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext.tsx';
import styles from './UserSettings.module.css';

const UserSettings = () => {
  const { user } = useAuth();
  const [userData, setUserData] = useState({
    username: '',
    name: '',
    bio: '',
    email: '',
  });

  const [editMode, setEditMode] = useState({
    username: false,
    bio: false,
    email: false,
    password: false
  });

  const [formValues, setFormValues] = useState({
    username: '',
    name: '',
    bio: '',
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [message, setMessage] = useState({ type: '', text: '' });
  const [modalErrors, setModalErrors] = useState({
    username: '',
    bio: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setMessage({ type: 'error', text: 'Brak tokenu autoryzacyjnego. Zaloguj się ponownie.' });
        return;
      }

      const response = await fetch('http://localhost:5000/api/user/profile', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUserData({
          username: data.username || '',
          name: data.name || '',
          bio: data.bio || '',
          email: data.email || ''
        });
      } else {
        const errorData = await response.json().catch(() => ({}));
        setMessage({ type: 'error', text: errorData.error || 'Nie udało się pobrać danych użytkownika.' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Wystąpił błąd podczas pobierania danych.' });
    }
  };

  const handleEdit = (field) => {
    setFormValues({
      ...formValues,
      [field]: userData[field] || ''
    });
    setEditMode({
      ...Object.keys(editMode).reduce((acc, key) => ({ ...acc, [key]: false }), {}),
      [field]: true
    });
    setMessage({ type: '', text: '' });
    setModalErrors({
      username: '',
      bio: '',
      email: '',
      password: ''
    });
  };

  const handleCancel = () => {
    setEditMode(Object.keys(editMode).reduce((acc, key) => ({ ...acc, [key]: false }), {}));
    setFormValues({
      username: '',
      name: '',
      bio: '',
      email: '',
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    setModalErrors({
      username: '',
      bio: '',
      email: '',
      password: ''
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormValues(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleUpdateUsername = async () => {
    setModalErrors(prev => ({ ...prev, username: '' }));
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/user/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ username: formValues.username })
      });

      if (response.ok) {
        const data = await response.json();
        setUserData(prev => ({ ...prev, username: data.username }));
        setMessage({ type: 'success', text: 'Nazwa użytkownika została zmieniona.' });
        handleCancel();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setModalErrors(prev => ({ ...prev, username: errorData.error || 'Nie udało się zmienić nazwy użytkownika.' }));
      }
    } catch (error) {
      setModalErrors(prev => ({ ...prev, username: 'Wystąpił błąd podczas aktualizacji nazwy użytkownika.' }));
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateName = async () => {
    setModalErrors(prev => ({ ...prev, name: '' }));
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/user/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ name: formValues.name })
      });

      if (response.ok) {
        const data = await response.json();
        setUserData(prev => ({ ...prev, name: data.name }));
        setMessage({ type: 'success', text: 'Nazwa użytkownika została zmieniona.' });
        handleCancel();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setModalErrors(prev => ({ ...prev, name: errorData.error || 'Nie udało się zmienić imienia i nazwiska.' }));
      }
    } catch (error) {
      setModalErrors(prev => ({ ...prev, name: 'Wystąpił błąd podczas aktualizacji imienia i nazwiska.' }));
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateBio = async () => {
    setModalErrors(prev => ({ ...prev, bio: '' }));
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/user/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ bio: formValues.bio })
      });

      if (response.ok) {
        const data = await response.json();
        setUserData(prev => ({ ...prev, bio: data.bio }));
        setMessage({ type: 'success', text: 'Opis został zmieniony.' });
        handleCancel();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setModalErrors(prev => ({ ...prev, bio: errorData.error || 'Nie udało się zmienić opisu.' }));
      }
    } catch (error) {
      setModalErrors(prev => ({ ...prev, bio: 'Wystąpił błąd podczas aktualizacji opisu.' }));
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
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/user/update-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: formValues.email,
          current_password: formValues.currentPassword
        })
      });

      if (response.ok) {
        const data = await response.json();
        setUserData(prev => ({ ...prev, email: data.email }));
        setMessage({ type: 'success', text: 'Adres email został zmieniony.' });
        handleCancel();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setModalErrors(prev => ({ ...prev, email: errorData.error || 'Nie udało się zmienić adresu email.' }));
      }
    } catch (error) {
      setModalErrors(prev => ({ ...prev, email: 'Wystąpił błąd podczas aktualizacji adresu email.' }));
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePassword = async () => {
    setModalErrors(prev => ({ ...prev, password: '' }));

    if (formValues.newPassword !== formValues.confirmPassword) {
      setModalErrors(prev => ({ ...prev, password: 'Nowe hasła nie są identyczne.' }));
      return;
    }

    if (!formValues.currentPassword) {
      setModalErrors(prev => ({ ...prev, password: 'Podaj aktualne hasło.' }));
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: formValues.currentPassword,
          new_password: formValues.newPassword
        })
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Hasło zostało zmienione.' });
        handleCancel();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setModalErrors(prev => ({ ...prev, password: errorData.error || 'Nie udało się zmienić hasła.' }));
      }
    } catch (error) {
      setModalErrors(prev => ({ ...prev, password: 'Wystąpił błąd podczas zmiany hasła.' }));
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

        <div className={styles['settings-divider']}></div>

        {editMode.name && (
          <div className={styles['modal-overlay']}>
            <div className={styles['edit-modal']}>
              <h2>Zmień nazwę użytkownika</h2>

              {modalErrors.name && (
                <div className={styles['modal-error']}>
                  {modalErrors.name}
                </div>
              )}

              <div className={styles['form-group']}>
                <label>Nazwa użytkownika</label>
                <input
                  type="text"
                  name="name"
                  value={formValues.name}
                  onChange={handleChange}
                />
              </div>
              <div className={styles['modal-actions']}>
                <button onClick={handleCancel}>Anuluj</button>
                <button onClick={handleUpdateName} disabled={loading}>
                  {loading ? 'Zapisywanie...' : 'Zapisz'}
                </button>
              </div>
            </div>
          </div>
        )}

        {editMode.bio && (
          <div className={styles['modal-overlay']}>
            <div className={styles['edit-modal']}>
              <h2>Zmień opis</h2>

              {modalErrors.bio && (
                <div className={styles['modal-error']}>
                  {modalErrors.bio}
                </div>
              )}

              <div className={styles['form-group']}>
                <label>O mnie</label>
                <textarea
                  name="bio"
                  value={formValues.bio}
                  onChange={handleChange}
                  rows="4"
                />
              </div>
              <div className={styles['modal-actions']}>
                <button onClick={handleCancel}>Anuluj</button>
                <button onClick={handleUpdateBio} disabled={loading}>
                  {loading ? 'Zapisywanie...' : 'Zapisz'}
                </button>
              </div>
            </div>
          </div>
        )}

        {editMode.email && (
          <div className={styles['modal-overlay']}>
            <div className={styles['edit-modal']}>
              <h2>Zmień adres email</h2>

              {modalErrors.email && (
                <div className={styles['modal-error']}>
                  {modalErrors.email}
                </div>
              )}

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
                <label>Aktualne hasło</label>
                <input
                  type="password"
                  name="currentPassword"
                  value={formValues.currentPassword}
                  onChange={handleChange}
                />
              </div>
              <div className={styles['modal-actions']}>
                <button onClick={handleCancel}>Anuluj</button>
                <button onClick={handleUpdateEmail} disabled={loading}>
                  {loading ? 'Zapisywanie...' : 'Zapisz'}
                </button>
              </div>
            </div>
          </div>
        )}

        {editMode.password && (
          <div className={styles['modal-overlay']}>
            <div className={styles['edit-modal']}>
              <h2>Zmień hasło</h2>

              {modalErrors.password && (
                <div className={styles['modal-error']}>
                  {modalErrors.password}
                </div>
              )}

              <div className={styles['form-group']}>
                <label>Aktualne hasło</label>
                <input
                  type="password"
                  name="currentPassword"
                  value={formValues.currentPassword}
                  onChange={handleChange}
                />
              </div>
              <div className={styles['form-group']}>
                <label>Nowe hasło</label>
                <input
                  type="password"
                  name="newPassword"
                  value={formValues.newPassword}
                  onChange={handleChange}
                />
              </div>
              <div className={styles['form-group']}>
                <label>Powtórz nowe hasło</label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formValues.confirmPassword}
                  onChange={handleChange}
                />
              </div>
              <div className={styles['modal-actions']}>
                <button onClick={handleCancel}>Anuluj</button>
                <button onClick={handleUpdatePassword} disabled={loading}>
                  {loading ? 'Zapisywanie...' : 'Zapisz'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserSettings;
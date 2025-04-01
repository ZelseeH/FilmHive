import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import styles from './LoginModal.module.css';

const LoginModal = ({ isOpen, onClose }) => {
  const { login } = useAuth();
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isLoginMode ? 'login' : 'register';
      const payload = isLoginMode
        ? { username, password }
        : { username, email, password };

      console.log(`Sending ${endpoint} request with:`, {
        username,
        email: !isLoginMode ? email : undefined
      });

      const response = await fetch(`http://localhost:5000/api/auth/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      console.log(`${endpoint} response:`, data);

      if (!response.ok) {
        throw new Error(data.error || 'Wystąpił błąd');
      }

      if (!data.access_token) {
        console.error("No access_token in response");
        throw new Error("Brak tokenu w odpowiedzi");
      }

      console.log("Calling login with:", {
        user: data.user,
        token: data.access_token ? "Token exists" : "No token"
      });

      login(data.user, data.access_token);

      console.log("Token saved:", localStorage.getItem('token') ? "Yes" : "No");

      onClose();
    } catch (err) {
      console.error("Login error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLoginMode(!isLoginMode);
    setError('');
    setUsername('');
    setEmail('');
    setPassword('');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className={styles['modal-overlay']}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className={styles['login-modal']}
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -50, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <button className={styles['close-button']} onClick={onClose}>×</button>
            <h2>{isLoginMode ? 'Zaloguj się' : 'Zarejestruj się'}</h2>

            {error && <div className={styles['error-message']}>{error}</div>}

            <form onSubmit={handleSubmit}>
              <div className={styles['form-group']}>
                <label htmlFor="username">Nazwa użytkownika</label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              {!isLoginMode && (
                <div className={styles['form-group']}>
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              )}

              <div className={styles['form-group']}>
                <label htmlFor="password">Hasło</label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <button
                type="submit"
                className={styles['submit-button']}
                disabled={loading}
              >
                {loading ? 'Przetwarzanie...' : isLoginMode ? 'Zaloguj' : 'Zarejestruj'}
              </button>
            </form>

            <p className={styles['toggle-mode']}>
              {isLoginMode ? 'Nie masz konta?' : 'Masz już konto?'}
              <button
                type="button"
                className={styles['toggle-button']}
                onClick={toggleMode}
              >
                {isLoginMode ? 'Zarejestruj się' : 'Zaloguj się'}
              </button>
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default LoginModal;
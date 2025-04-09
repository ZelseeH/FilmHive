// components/LoginModal/LoginModal.tsx
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import * as authService from './services/authService';
import styles from './LoginModal.module.css';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  const { login } = useAuth();
  const [isLoginMode, setIsLoginMode] = useState<boolean>(true);
  const [username, setUsername] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let data;

      if (isLoginMode) {
        data = await authService.login(username, password);
      } else {
        data = await authService.register(username, email, password);
      }

      if (!data.access_token) {
        throw new Error("Brak tokenu w odpowiedzi");
      }

      login(data.user, data.access_token);
      onClose();
    } catch (err: any) {
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

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import * as authService from './services/authService';
import PasswordStrengthMeter from './components/PasswordStrengthMeter/PasswordStrengthMeter';
import SocialLogin from './components/SocialLogin/SocialLogin';
import ForgotPassword from './components/ForgotPassword/ForgotPassword';
import styles from './LoginPage.module.css';
import logo from './FilmHive.png';

const LoginPage: React.FC = () => {
    const { login, user } = useAuth();
    const navigate = useNavigate();
    const [isLoginMode, setIsLoginMode] = useState<boolean>(true);
    const [showForgotPassword, setShowForgotPassword] = useState<boolean>(false);
    const [username, setUsername] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [confirmPassword, setConfirmPassword] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [confirmPasswordError, setConfirmPasswordError] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);

    // Sprawdzenie czy użytkownik jest zalogowany (zamiast isAuthenticated)
    const isAuthenticated = user !== null;

    // Przekierowanie zalogowanych użytkowników
    useEffect(() => {
        if (isAuthenticated) {
            navigate('/', { replace: true });
        }
    }, [isAuthenticated, navigate]);

    // Jeśli użytkownik jest zalogowany, nie renderuj komponentu
    if (isAuthenticated) {
        return null;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setConfirmPasswordError('');
        setLoading(true);

        // Walidacja potwierdzenia hasła dla rejestracji
        if (!isLoginMode) {
            if (password !== confirmPassword) {
                setConfirmPasswordError('Hasła nie są takie same');
                setLoading(false);
                return;
            } else {
                setConfirmPasswordError('');
            }
        }

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

            const refreshToken = data.refresh_token || '';
            const loginSuccess = login(data.user, data.access_token, refreshToken);

            if (loginSuccess) {
                navigate('/', { replace: true });
            }
        } catch (err: any) {
            console.error("Auth error:", err);
            if (err.response && err.response.status === 401) {
                setError("Niepoprawny login lub hasło.");
            } else if (err.response && err.response.status === 403) {
                setError("Twoje konto zostało zawieszone lub dezaktywowane przez administratora.");
            } else if (err.response && err.response.status === 409) {
                setError("Email albo Nazwa użytkownika jest już zajęta.");
            } else if (err.message) {
                setError(err.message);
            } else {
                setError("Wystąpił nieznany błąd podczas logowania.");
            }
        } finally {
            setLoading(false);
        }
    };

    const toggleMode = () => {
        setIsLoginMode(!isLoginMode);
        setError('');
        setConfirmPasswordError('');
        setUsername('');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
        setShowForgotPassword(false);
    };

    if (showForgotPassword) {
        return <ForgotPassword onBack={() => setShowForgotPassword(false)} />;
    }

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                {/* Lewa strona - Desktop */}
                <motion.div
                    className={`${styles.leftSide} ${!isLoginMode ? styles.logoSide : styles.formSide}`}
                    initial={false}
                    animate={{
                        x: isLoginMode ? 0 : 0,
                        opacity: 1
                    }}
                    transition={{ duration: 0.6, ease: "easeInOut" }}
                >
                    <AnimatePresence mode="wait">
                        {isLoginMode ? (
                            <motion.div
                                key="login-form"
                                initial={{ opacity: 0, x: -50 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -50 }}
                                transition={{ duration: 0.6 }}
                                className={styles.formContainer}
                            >
                                <h1>Zaloguj się</h1>
                                <p className={styles.subtitle}>Witaj ponownie! Zaloguj się do swojego konta</p>

                                {error && <div className={styles.errorMessage}>{error}</div>}

                                <form onSubmit={handleSubmit} className={styles.form}>
                                    <div className={styles.formGroup}>
                                        <label htmlFor="username">Nazwa użytkownika</label>
                                        <input
                                            type="text"
                                            id="username"
                                            value={username}
                                            onChange={(e) => setUsername(e.target.value)}
                                            required
                                            className={styles.input}
                                        />
                                    </div>

                                    <div className={styles.formGroup}>
                                        <label htmlFor="password">Hasło</label>
                                        <input
                                            type="password"
                                            id="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            required
                                            className={styles.input}
                                        />
                                    </div>

                                    <button
                                        type="button"
                                        className={styles.forgotPassword}
                                        onClick={() => setShowForgotPassword(true)}
                                    >
                                        Zapomniałeś hasła?
                                    </button>

                                    <button
                                        type="submit"
                                        className={styles.submitButton}
                                        disabled={loading}
                                    >
                                        {loading ? 'Logowanie...' : 'Zaloguj się'}
                                    </button>
                                </form>

                                <SocialLogin />

                                <p className={styles.toggleText}>
                                    Nie masz konta?{' '}
                                    <button
                                        type="button"
                                        className={styles.toggleButton}
                                        onClick={toggleMode}
                                    >
                                        Zarejestruj się
                                    </button>
                                </p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="logo-side"
                                initial={{ opacity: 0, x: -50 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -50 }}
                                transition={{ duration: 0.6 }}
                                className={styles.logoContainer}
                            >
                                <div className={styles.logo}>
                                    <img src={logo} alt="FilmHive Logo" className={styles.logoImage} />
                                    <h2 className={styles.serviceName}>FilmHive</h2>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>

                {/* Prawa strona - Desktop */}
                <motion.div
                    className={`${styles.rightSide} ${isLoginMode ? styles.logoSide : styles.formSide}`}
                    initial={false}
                    animate={{
                        x: isLoginMode ? 0 : 0,
                        opacity: 1
                    }}
                    transition={{ duration: 0.6, ease: "easeInOut" }}
                >
                    <AnimatePresence mode="wait">
                        {isLoginMode ? (
                            <motion.div
                                key="logo-side"
                                initial={{ opacity: 0, x: 50 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 50 }}
                                transition={{ duration: 0.6 }}
                                className={styles.logoContainer}
                            >
                                <div className={styles.logo}>
                                    <img src={logo} alt="FilmHive Logo" className={styles.logoImage} />
                                    <h2 className={styles.serviceName}>FilmHive</h2>
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="register-form"
                                initial={{ opacity: 0, x: 50 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 50 }}
                                transition={{ duration: 0.6 }}
                                className={styles.formContainer}
                            >
                                <h1>Zarejestruj się</h1>
                                <p className={styles.subtitle}>Utwórz nowe konto i rozpocznij swoją przygodę</p>

                                {error && <div className={styles.errorMessage}>{error}</div>}

                                <form onSubmit={handleSubmit} className={styles.form}>
                                    <div className={styles.formGroup}>
                                        <label htmlFor="reg-username">Nazwa użytkownika</label>
                                        <input
                                            type="text"
                                            id="reg-username"
                                            value={username}
                                            onChange={(e) => setUsername(e.target.value)}
                                            required
                                            className={styles.input}
                                        />
                                    </div>

                                    <div className={styles.formGroup}>
                                        <label htmlFor="reg-email">Email</label>
                                        <input
                                            type="email"
                                            id="reg-email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            required
                                            className={styles.input}
                                        />
                                    </div>

                                    <div className={styles.formGroup}>
                                        <label htmlFor="reg-password">Hasło</label>
                                        <input
                                            type="password"
                                            id="reg-password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            required
                                            className={styles.input}
                                        />
                                        <PasswordStrengthMeter password={password} />
                                    </div>

                                    <div className={styles.formGroup}>
                                        <label htmlFor="reg-confirm-password">Potwierdź hasło</label>
                                        <input
                                            type="password"
                                            id="reg-confirm-password"
                                            value={confirmPassword}
                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                            required
                                            className={styles.input}
                                        />
                                        {confirmPasswordError && (
                                            <div className={styles.errorMessage}>{confirmPasswordError}</div>
                                        )}
                                    </div>

                                    <button
                                        type="submit"
                                        className={styles.submitButton}
                                        disabled={loading}
                                    >
                                        {loading ? 'Rejestracja...' : 'Zarejestruj się'}
                                    </button>
                                </form>

                                <SocialLogin />

                                <p className={styles.toggleText}>
                                    Masz już konto?{' '}
                                    <button
                                        type="button"
                                        className={styles.toggleButton}
                                        onClick={toggleMode}
                                    >
                                        Zaloguj się
                                    </button>
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>

                {/* Wersja mobilna */}
                <div className={styles.mobileContainer}>
                    <div className={styles.mobileLogo}>
                        <img src={logo} alt="FilmHive Logo" className={styles.logoImage} />
                        <h2 className={styles.serviceName}>FilmHive</h2>
                    </div>

                    <AnimatePresence mode="wait">
                        <motion.div
                            key={isLoginMode ? 'mobile-login' : 'mobile-register'}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.4 }}
                            className={styles.mobileForm}
                        >
                            <h1>{isLoginMode ? 'Zaloguj się' : 'Zarejestruj się'}</h1>

                            {error && <div className={styles.errorMessage}>{error}</div>}

                            <form onSubmit={handleSubmit} className={styles.form}>
                                <div className={styles.formGroup}>
                                    <label htmlFor="mobile-username">Nazwa użytkownika</label>
                                    <input
                                        type="text"
                                        id="mobile-username"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        required
                                        className={styles.input}
                                    />
                                </div>

                                {!isLoginMode && (
                                    <div className={styles.formGroup}>
                                        <label htmlFor="mobile-email">Email</label>
                                        <input
                                            type="email"
                                            id="mobile-email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            required
                                            className={styles.input}
                                        />
                                    </div>
                                )}

                                <div className={styles.formGroup}>
                                    <label htmlFor="mobile-password">Hasło</label>
                                    <input
                                        type="password"
                                        id="mobile-password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        className={styles.input}
                                    />
                                    {!isLoginMode && <PasswordStrengthMeter password={password} />}
                                </div>

                                {!isLoginMode && (
                                    <div className={styles.formGroup}>
                                        <label htmlFor="mobile-confirm-password">Potwierdź hasło</label>
                                        <input
                                            type="password"
                                            id="mobile-confirm-password"
                                            value={confirmPassword}
                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                            required
                                            className={styles.input}
                                        />
                                        {confirmPasswordError && (
                                            <div className={styles.errorMessage}>{confirmPasswordError}</div>
                                        )}
                                    </div>
                                )}

                                {isLoginMode && (
                                    <button
                                        type="button"
                                        className={styles.forgotPassword}
                                        onClick={() => setShowForgotPassword(true)}
                                    >
                                        Zapomniałeś hasła?
                                    </button>
                                )}

                                <button
                                    type="submit"
                                    className={styles.submitButton}
                                    disabled={loading}
                                >
                                    {loading
                                        ? (isLoginMode ? 'Logowanie...' : 'Rejestracja...')
                                        : (isLoginMode ? 'Zaloguj się' : 'Zarejestruj się')
                                    }
                                </button>
                            </form>

                            <SocialLogin />

                            <p className={styles.toggleText}>
                                {isLoginMode ? 'Nie masz konta?' : 'Masz już konto?'}
                                <button
                                    type="button"
                                    className={styles.toggleButton}
                                    onClick={toggleMode}
                                >
                                    {isLoginMode ? 'Zarejestruj się' : 'Zaloguj się'}
                                </button>
                            </p>
                        </motion.div>
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;

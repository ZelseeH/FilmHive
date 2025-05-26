// components/ForgotPassword.tsx
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import styles from './ForgotPassword.module.css';
import logo from '../../FilmHive.png';


interface ForgotPasswordProps {
    onBack: () => void;
}

const ForgotPassword: React.FC<ForgotPasswordProps> = ({ onBack }) => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Implementacja wysyłania emaila resetującego hasło
            const response = await fetch('http://localhost:5000/api/auth/forgot-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            if (!response.ok) {
                throw new Error('Wystąpił błąd podczas wysyłania emaila.');
            }

            setSuccess(true);
        } catch (err: any) {
            setError(err.message || 'Wystąpił błąd podczas wysyłania emaila.');
        } finally {
            setLoading(false);
        }
    };

    const handleBackToLogin = () => {
        navigate('/login', { replace: true });
    };

    return (
        <div className={styles.container}>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={styles.content}
            >
                <div className={styles.logoSection}>
                    <img src={logo} alt="FilmHive Logo" className={styles.logoImage} />
                    <h2 className={styles.serviceName}>Invincible</h2>
                </div>

                <div className={styles.formSection}>
                    <button className={styles.backButton} onClick={onBack}>
                        ← Powrót do logowania
                    </button>

                    {!success ? (
                        <>
                            <h1>Resetuj hasło</h1>
                            <p className={styles.subtitle}>
                                Podaj swój adres email, a wyślemy Ci link do resetowania hasła.
                            </p>

                            {error && <div className={styles.errorMessage}>{error}</div>}

                            <form onSubmit={handleSubmit} className={styles.form}>
                                <div className={styles.formGroup}>
                                    <label htmlFor="reset-email">Adres email</label>
                                    <input
                                        type="email"
                                        id="reset-email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        className={styles.input}
                                        placeholder="twoj@email.com"
                                    />
                                </div>

                                <button
                                    type="submit"
                                    className={styles.submitButton}
                                    disabled={loading}
                                >
                                    {loading ? 'Wysyłanie...' : 'Wyślij link resetujący'}
                                </button>
                            </form>
                        </>
                    ) : (
                        <div className={styles.successContainer}>
                            <div className={styles.successIcon}>✓</div>
                            <h2>Email został wysłany!</h2>
                            <p className={styles.successText}>
                                Sprawdź swoją skrzynkę pocztową i kliknij w link, aby zresetować hasło.
                                Link będzie ważny przez 24 godziny.
                            </p>
                            <button className={styles.submitButton} onClick={handleBackToLogin}>
                                Powrót do logowania
                            </button>
                        </div>
                    )}
                </div>
            </motion.div>
        </div>
    );
};

export default ForgotPassword;

import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { userService } from '../../services/userService';
import styles from './UsersAddPage.module.css';
import { Toast } from 'primereact/toast';
import { ConfirmDialog } from 'primereact/confirmdialog';

interface FormData {
    username: string;
    email: string;
    password: string;
    confirmPassword: string;
    name: string;
    bio: string;
    role: number;
    is_active: boolean;
}

const UsersAddPage: React.FC = () => {
    const navigate = useNavigate();
    const toast = useRef<Toast>(null);

    const [formData, setFormData] = useState<FormData>({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        name: '',
        bio: '',
        role: 3, // Domyślnie zwykły użytkownik
        is_active: true
    });

    const [errors, setErrors] = useState<Record<string, string>>({});
    const [loading, setLoading] = useState<boolean>(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        // Wyczyść błąd dla tego pola
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: checked
        }));
    };

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        // Walidacja nazwy użytkownika
        if (!formData.username.trim()) {
            newErrors.username = 'Nazwa użytkownika jest wymagana';
        } else if (formData.username.length < 3) {
            newErrors.username = 'Nazwa użytkownika musi mieć co najmniej 3 znaki';
        }

        // Walidacja emaila
        if (!formData.email.trim()) {
            newErrors.email = 'Email jest wymagany';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Podaj prawidłowy adres email';
        }

        // Walidacja hasła
        if (!formData.password) {
            newErrors.password = 'Hasło jest wymagane';
        } else if (formData.password.length < 8) {
            newErrors.password = 'Hasło musi mieć co najmniej 8 znaków';
        }

        // Walidacja potwierdzenia hasła
        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Hasła nie są zgodne';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        try {
            setLoading(true);

            // Przygotowanie danych do wysłania
            const userData = {
                username: formData.username,
                email: formData.email,
                password: formData.password,
                name: formData.name,
                bio: formData.bio,
                role: parseInt(formData.role.toString()),
                is_active: formData.is_active
            };

            const result = await userService.createUser(userData);

            toast.current?.show({
                severity: 'success',
                summary: 'Sukces',
                detail: 'Użytkownik został pomyślnie utworzony',
                life: 3000
            });

            // Przekieruj do szczegółów nowego użytkownika
            setTimeout(() => {
                navigate(`/dashboardpanel/users/manage`);
            }, 1500);

        } catch (err: any) {
            toast.current?.show({
                severity: 'error',
                summary: 'Błąd',
                detail: err.message || 'Nie udało się utworzyć użytkownika',
                life: 5000
            });
            console.error('Error creating user:', err);
        } finally {
            setLoading(false);
        }
    };

    const getRoleName = (roleId: number): string => {
        switch (roleId) {
            case 1: return 'Administrator';
            case 2: return 'Moderator';
            case 3: return 'Użytkownik';
            default: return 'Nieznana';
        }
    };

    return (
        <div className={styles.container}>
            <Toast ref={toast} />
            <ConfirmDialog />

            <div className={styles.header}>


                <h1 className={styles.title}>Dodaj nowego użytkownika</h1>
            </div>

            <div className={styles.formCard}>
                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.formGrid}>
                        <div className={styles.formGroup}>
                            <label htmlFor="username">Nazwa użytkownika*</label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                className={`${styles.input} ${errors.username ? styles.inputError : ''}`}
                            />
                            {errors.username && <div className={styles.errorMessage}>{errors.username}</div>}
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="email">Email*</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                className={`${styles.input} ${errors.email ? styles.inputError : ''}`}
                            />
                            {errors.email && <div className={styles.errorMessage}>{errors.email}</div>}
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="password">Hasło*</label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                className={`${styles.input} ${errors.password ? styles.inputError : ''}`}
                            />
                            {errors.password && <div className={styles.errorMessage}>{errors.password}</div>}
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="confirmPassword">Potwierdź hasło*</label>
                            <input
                                type="password"
                                id="confirmPassword"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                className={`${styles.input} ${errors.confirmPassword ? styles.inputError : ''}`}
                            />
                            {errors.confirmPassword && <div className={styles.errorMessage}>{errors.confirmPassword}</div>}
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="name">Imię i nazwisko</label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                className={styles.input}
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="role">Rola</label>
                            <select
                                id="role"
                                name="role"
                                value={formData.role}
                                onChange={handleChange}
                                className={styles.select}
                            >
                                <option value={1}>Administrator</option>
                                <option value={2}>Moderator</option>
                                <option value={3}>Użytkownik</option>
                            </select>
                        </div>

                        <div className={`${styles.formGroup} ${styles.fullWidth}`}>
                            <label htmlFor="bio">Bio</label>
                            <textarea
                                id="bio"
                                name="bio"
                                value={formData.bio}
                                onChange={handleChange}
                                className={styles.textarea}
                                rows={4}
                            />
                        </div>

                        <div className={`${styles.formGroup} ${styles.checkboxGroup}`}>
                            <label className={styles.checkboxLabel}>
                                <input
                                    type="checkbox"
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleCheckboxChange}
                                    className={styles.checkbox}
                                />
                                <span>Aktywny użytkownik</span>
                            </label>
                        </div>
                    </div>

                    <div className={styles.formActions}>
                        <button
                            type="submit"
                            className={styles.submitButton}
                            disabled={loading}
                        >
                            {loading ? 'Tworzenie...' : 'Utwórz użytkownika'}
                        </button>
                        <button
                            type="button"
                            className={styles.cancelButton}
                            onClick={() => navigate('/dashboardpanel/users/manage')}
                            disabled={loading}
                        >
                            Anuluj
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default UsersAddPage;

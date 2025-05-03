// pages/Dashboard/components/UserDetails.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../contexts/AuthContext';
import { userService } from '../../services/userService';
import { useInlineEdit } from '../../hooks/useInlineEdit';
import styles from './UserDetails.module.css';

interface UserDetailsParams {
    id: string;
}

const UserDetails: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { getToken } = useAuth();
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [userData, setUserData] = useState<any>(null);
    const [password, setPassword] = useState<string>('');
    const [confirmPassword, setConfirmPassword] = useState<string>('');
    const [showPasswordForm, setShowPasswordForm] = useState<boolean>(false);

    // Pobieranie ID użytkownika z parametru URL
    const userId = id?.split('-')[0];

    useEffect(() => {
        if (userId) {
            fetchUserDetails(userId);
        }
    }, [userId]);

    const fetchUserDetails = async (userId: string) => {
        try {
            setLoading(true);
            const data = await userService.getUserDetails(userId);
            setUserData(data);
            setError(null);
        } catch (err: any) {
            setError(err.message);
            console.error('Error fetching user details:', err);
        } finally {
            setLoading(false);
        }
    };

    // Jeśli dane użytkownika nie są jeszcze załadowane, nie inicjalizuj hooka
    if (!userData && !loading) {
        return <div className={styles.errorMessage}>Nie można załadować danych użytkownika</div>;
    }

    if (loading) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p>Ładowanie danych użytkownika...</p>
            </div>
        );
    }

    return (
        <UserDetailsContent
            userData={userData}
            userId={userId as string}
            error={error}
            onRefresh={() => fetchUserDetails(userId as string)}
            navigate={navigate}
        />
    );
};

interface UserDetailsContentProps {
    userData: any;
    userId: string;
    error: string | null;
    onRefresh: () => void;
    navigate: any;
}

const UserDetailsContent: React.FC<UserDetailsContentProps> = ({
    userData,
    userId,
    error,
    onRefresh,
    navigate
}) => {
    const { user: currentUser } = useAuth();
    const isCurrentUser = userData.id === currentUser?.id;
    const { fields, toggleEdit, updateField, cancelEdit, getValues, setInputRef } = useInlineEdit(userData);
    const [password, setPassword] = useState<string>('');
    const [confirmPassword, setConfirmPassword] = useState<string>('');
    const [showPasswordForm, setShowPasswordForm] = useState<boolean>(false);
    const [passwordError, setPasswordError] = useState<string | null>(null);
    const [saveLoading, setSaveLoading] = useState<Record<string, boolean>>({});
    const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

    const handleFieldSave = async (fieldName: string) => {
        try {
            setSaveLoading(prev => ({ ...prev, [fieldName]: true }));
            setFieldErrors(prev => ({ ...prev, [fieldName]: '' }));

            const value = fields[fieldName].value;
            await userService.updateUserField(userId, fieldName, value);

            // Zakończ tryb edycji
            toggleEdit(fieldName);

            // Odśwież dane użytkownika
            onRefresh();
        } catch (err: any) {
            setFieldErrors(prev => ({ ...prev, [fieldName]: err.message }));
            console.error(`Error updating ${fieldName}:`, err);
        } finally {
            setSaveLoading(prev => ({ ...prev, [fieldName]: false }));
        }
    };

    const handleRoleChange = async (newRole: number) => {
        try {
            setSaveLoading(prev => ({ ...prev, 'role': true }));
            await userService.updateUserRole(userId, newRole);
            onRefresh();
        } catch (err: any) {
            setFieldErrors(prev => ({ ...prev, 'role': err.message }));
            console.error('Error updating role:', err);
        } finally {
            setSaveLoading(prev => ({ ...prev, 'role': false }));
        }
    };

    const handleStatusChange = async (isActive: boolean) => {
        try {
            setSaveLoading(prev => ({ ...prev, 'is_active': true }));
            await userService.updateUserStatus(userId, isActive);
            onRefresh();
        } catch (err: any) {
            setFieldErrors(prev => ({ ...prev, 'is_active': err.message }));
            console.error('Error updating status:', err);
        } finally {
            setSaveLoading(prev => ({ ...prev, 'is_active': false }));
        }
    };

    const handlePasswordChange = async () => {
        if (password !== confirmPassword) {
            setPasswordError('Hasła nie są zgodne');
            return;
        }

        if (password.length < 8) {
            setPasswordError('Hasło musi mieć co najmniej 8 znaków');
            return;
        }

        try {
            setSaveLoading(prev => ({ ...prev, 'password': true }));
            setPasswordError(null);

            await userService.updateUserPassword(userId, password);

            setPassword('');
            setConfirmPassword('');
            setShowPasswordForm(false);

            // Odśwież dane użytkownika
            onRefresh();
        } catch (err: any) {
            setPasswordError(err.message);
            console.error('Error updating password:', err);
        } finally {
            setSaveLoading(prev => ({ ...prev, 'password': false }));
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

    const formatDate = (dateString?: string): string => {
        if (!dateString) return 'Nigdy';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('pl-PL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    };

    const renderEditableField = (fieldName: string, label: string, type: 'text' | 'textarea' | 'email' = 'text') => {
        const field = fields[fieldName];

        if (!field) return null;

        return (
            <div className={styles.detailItem}>
                <h3>{label}:</h3>
                {field.isEditing ? (
                    <div className={styles.editableFieldWrapper}>
                        {type === 'textarea' ? (
                            <textarea
                                ref={(el) => setInputRef(fieldName, el)}
                                value={field.value || ''}
                                onChange={(e) => updateField(fieldName, e.target.value)}
                                className={styles.editableInput}
                                rows={4}
                            />
                        ) : (
                            <input
                                type={type}
                                ref={(el) => setInputRef(fieldName, el)}
                                value={field.value || ''}
                                onChange={(e) => updateField(fieldName, e.target.value)}
                                className={styles.editableInput}
                            />
                        )}
                        <div className={styles.editActions}>
                            <button
                                onClick={() => handleFieldSave(fieldName)}
                                className={styles.saveButton}
                                disabled={saveLoading[fieldName]}
                            >
                                {saveLoading[fieldName] ? 'Zapisywanie...' : 'Zapisz'}
                            </button>
                            <button
                                onClick={() => toggleEdit(fieldName)}
                                className={styles.cancelButton}
                            >
                                Anuluj
                            </button>
                        </div>
                        {fieldErrors[fieldName] && (
                            <div className={styles.fieldError}>{fieldErrors[fieldName]}</div>
                        )}
                    </div>
                ) : (
                    <p
                        className={styles.editableText}
                        onClick={() => toggleEdit(fieldName)}
                    >
                        {field.value || <span className={styles.emptyValue}>Brak danych</span>}
                        <span className={styles.editIcon}>✎</span>
                    </p>
                )}
            </div>
        );
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <button
                    className={styles.backButton}
                    onClick={() => navigate('/dashboard/users')}
                >
                    &larr; Powrót do listy
                </button>

                <h1 className={styles.title}>
                    Szczegóły użytkownika: {userData.username}
                    {isCurrentUser && <span className={styles.currentUserBadge}> (Ty)</span>}
                </h1>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div className={styles.userDetailsCard}>
                <div className={styles.userHeader}>
                    {userData.profile_picture ? (
                        <img src={userData.profile_picture} alt={userData.username} className={styles.userAvatar} />
                    ) : (
                        <div className={styles.userAvatarPlaceholder}>
                            {userData.username.charAt(0).toUpperCase()}
                        </div>
                    )}
                    <div className={styles.userInfo}>
                        <h2>{userData.username}</h2>
                        <p className={styles.userRole}>{getRoleName(userData.role)}</p>
                        <p className={styles.userStatus}>
                            <span className={userData.is_active ? styles.activeStatus : styles.inactiveStatus}>
                                {userData.is_active ? 'Aktywny' : 'Nieaktywny'}
                            </span>
                        </p>
                    </div>
                </div>

                <div className={styles.userDetailsContent}>
                    <div className={styles.userDetailsGrid}>
                        {renderEditableField('username', 'Nazwa użytkownika')}
                        {renderEditableField('email', 'Email', 'email')}
                        {renderEditableField('name', 'Imię i nazwisko')}
                        <div className={`${styles.detailItem} ${styles.bioField}`}>
                            {renderEditableField('bio', 'Bio', 'textarea')}
                        </div>

                        <div className={styles.detailItem}>
                            <h3>Rola:</h3>
                            {isCurrentUser ? (
                                <div className={styles.roleText}>
                                    {getRoleName(userData.role)}
                                    <span className={styles.tooltipText}>Nie możesz zmienić własnej roli</span>
                                </div>
                            ) : (
                                <div className={styles.selectWrapper}>
                                    <select
                                        value={userData.role}
                                        onChange={(e) => handleRoleChange(Number(e.target.value))}
                                        className={styles.select}
                                        disabled={saveLoading['role']}
                                    >
                                        <option value={1}>Administrator</option>
                                        <option value={2}>Moderator</option>
                                        <option value={3}>Użytkownik</option>
                                    </select>
                                    {saveLoading['role'] && <span className={styles.miniSpinner}></span>}
                                </div>
                            )}
                            {fieldErrors['role'] && (
                                <div className={styles.fieldError}>{fieldErrors['role']}</div>
                            )}
                        </div>

                        <div className={styles.detailItem}>
                            <h3>Status:</h3>
                            {isCurrentUser ? (
                                <div className={styles.statusText}>
                                    <span className={userData.is_active ? styles.activeStatus : styles.inactiveStatus}>
                                        {userData.is_active ? 'Aktywny' : 'Nieaktywny'}
                                    </span>
                                    <span className={styles.tooltipText}>Nie możesz zmienić statusu własnego konta</span>
                                </div>
                            ) : (
                                <div className={styles.statusToggle}>
                                    <button
                                        onClick={() => handleStatusChange(true)}
                                        className={`${styles.statusButton} ${userData.is_active ? styles.statusButtonActive : ''}`}
                                        disabled={userData.is_active || saveLoading['is_active']}
                                    >
                                        Aktywny
                                    </button>
                                    <button
                                        onClick={() => handleStatusChange(false)}
                                        className={`${styles.statusButton} ${!userData.is_active ? styles.statusButtonActive : ''}`}
                                        disabled={!userData.is_active || saveLoading['is_active']}
                                    >
                                        Nieaktywny
                                    </button>
                                    {saveLoading['is_active'] && <span className={styles.miniSpinner}></span>}
                                </div>
                            )}
                            {fieldErrors['is_active'] && (
                                <div className={styles.fieldError}>{fieldErrors['is_active']}</div>
                            )}
                        </div>

                        <div className={styles.detailItem}>
                            <h3>Data rejestracji:</h3>
                            <p>{formatDate(userData.registration_date)}</p>
                        </div>

                        <div className={styles.detailItem}>
                            <h3>Ostatnie logowanie:</h3>
                            <p>{formatDate(userData.last_login)}</p>
                        </div>

                        <div className={`${styles.detailItem} ${styles.fullWidth}`}>
                            <h3>Hasło:</h3>
                            {showPasswordForm ? (
                                <div className={styles.passwordForm}>
                                    <div className={styles.passwordFields}>
                                        <div className={styles.formGroup}>
                                            <label htmlFor="password">Nowe hasło:</label>
                                            <input
                                                id="password"
                                                type="password"
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                className={styles.input}
                                            />
                                        </div>
                                        <div className={styles.formGroup}>
                                            <label htmlFor="confirmPassword">Potwierdź hasło:</label>
                                            <input
                                                id="confirmPassword"
                                                type="password"
                                                value={confirmPassword}
                                                onChange={(e) => setConfirmPassword(e.target.value)}
                                                className={styles.input}
                                            />
                                        </div>
                                    </div>
                                    <div className={styles.passwordActions}>
                                        <button
                                            onClick={handlePasswordChange}
                                            className={styles.saveButton}
                                            disabled={saveLoading['password']}
                                        >
                                            {saveLoading['password'] ? 'Zapisywanie...' : 'Zmień hasło'}
                                        </button>
                                        <button
                                            onClick={() => {
                                                setShowPasswordForm(false);
                                                setPassword('');
                                                setConfirmPassword('');
                                                setPasswordError(null);
                                            }}
                                            className={styles.cancelButton}
                                        >
                                            Anuluj
                                        </button>
                                    </div>
                                    {passwordError && (
                                        <div className={styles.fieldError}>{passwordError}</div>
                                    )}
                                </div>
                            ) : (
                                <button
                                    onClick={() => setShowPasswordForm(true)}
                                    className={styles.changePasswordButton}
                                >
                                    Zmień hasło
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserDetails;

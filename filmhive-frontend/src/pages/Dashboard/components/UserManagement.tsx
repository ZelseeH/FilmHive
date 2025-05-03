import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import Pagination from '../../../components/ui/Pagination';
import styles from './UserManagement.module.css';
import { createSlug } from '../../../utils/formatters';

interface User {
    id: string;
    username: string;
    email: string;
    role: number;
    is_active: boolean;
    registration_date: string;
    last_login?: string;
    is_current_user?: boolean;
}

interface ApiResponse {
    users: User[];
    pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
    };
}

const UserManagement: React.FC = () => {
    const { getToken, user: currentUser } = useAuth();
    const navigate = useNavigate();
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [totalPages, setTotalPages] = useState<number>(1);
    const [totalUsers, setTotalUsers] = useState<number>(0);
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [filterRole, setFilterRole] = useState<number | null>(null);
    const perPage = 10;

    const fetchUsers = async (page: number = 1) => {
        try {
            setLoading(true);
            const token = getToken();

            let url = `http://localhost:5000/api/admin/users?page=${page}&per_page=${perPage}`;

            if (searchQuery) {
                url += `&search=${encodeURIComponent(searchQuery)}`;
            }

            if (filterRole !== null) {
                url += `&role=${filterRole}`;
            }

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Nie udało się pobrać listy użytkowników');
            }

            const data: ApiResponse = await response.json();

            // Oznaczamy obecnie zalogowanego użytkownika
            const sortedUsers = [...data.users].map(user => ({
                ...user,
                is_current_user: user.id === currentUser?.id
            })).sort((a, b) => {
                if (a.role !== b.role) {
                    return a.role - b.role;
                }
                return a.username.localeCompare(b.username);
            });

            setUsers(sortedUsers);

            if (data.pagination) {
                setCurrentPage(data.pagination.page || 1);
                setTotalPages(data.pagination.total_pages || 1);
                setTotalUsers(data.pagination.total || 0);
            } else {
                setCurrentPage(1);
                setTotalPages(1);
                setTotalUsers(sortedUsers.length);
            }

            setError(null);
        } catch (err: any) {
            setError(err.message);
            console.error('Error fetching users:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, [filterRole]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        fetchUsers(1);
    };

    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage);
        fetchUsers(newPage);
    };

    const changeUserRole = async (userId: string, newRole: number) => {
        try {
            setLoading(true);
            const token = getToken();

            const response = await fetch(`http://localhost:5000/api/admin/users/${userId}/role`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ role: newRole })
            });

            if (!response.ok) {
                throw new Error('Nie udało się zmienić roli użytkownika');
            }

            fetchUsers(currentPage);
        } catch (err: any) {
            setError(err.message);
            console.error('Error changing user role:', err);
        } finally {
            setLoading(false);
        }
    };

    const toggleUserStatus = async (userId: string, isActive: boolean) => {
        try {
            setLoading(true);
            const token = getToken();

            const response = await fetch(`http://localhost:5000/api/admin/users/${userId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ is_active: !isActive })
            });

            if (!response.ok) {
                throw new Error('Nie udało się zmienić statusu użytkownika');
            }

            fetchUsers(currentPage);
        } catch (err: any) {
            setError(err.message);
            console.error('Error toggling user status:', err);
        } finally {
            setLoading(false);
        }
    };

    const getRoleName = (role: number): string => {
        switch (role) {
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

    const navigateToUserDetails = (user: User) => {
        const userSlug = createSlug(user.username);
        navigate(`/dashboard/users/${user.id}-${userSlug}`);
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Zarządzanie Użytkownikami</h1>
                <p className={styles.description}>
                    Przeglądaj, filtruj i zarządzaj kontami użytkowników w systemie.
                </p>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div className={styles.filtersContainer}>
                <form onSubmit={handleSearch} className={styles.searchForm}>
                    <input
                        type="text"
                        placeholder="Szukaj po nazwie użytkownika lub email"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className={styles.searchInput}
                    />
                    <button type="submit" className={styles.searchButton}>Szukaj</button>
                </form>

                <div className={styles.roleFilter}>
                    <label>Filtruj po roli:</label>
                    <select
                        value={filterRole === null ? '' : filterRole}
                        onChange={(e) => setFilterRole(e.target.value ? Number(e.target.value) : null)}
                        className={styles.select}
                    >
                        <option value="">Wszystkie role</option>
                        <option value="1">Administrator</option>
                        <option value="2">Moderator</option>
                        <option value="3">Użytkownik</option>
                    </select>
                </div>
            </div>

            {loading && users.length === 0 ? (
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Ładowanie użytkowników...</p>
                </div>
            ) : (
                <>
                    <div className={styles.tableContainer}>
                        <table className={styles.usersTable}>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Nazwa użytkownika</th>
                                    <th>Email</th>
                                    <th>Rola</th>
                                    <th>Status</th>
                                    <th>Data rejestracji</th>
                                    <th>Ostatnie logowanie</th>
                                    <th>Akcje</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(user => (
                                    <tr
                                        key={user.id}
                                        className={`${!user.is_active ? styles.inactiveUser : ''} 
                                                  ${user.role === 2 ? styles.moderatorRow : ''} 
                                                  ${user.is_current_user ? styles.currentUserRow : ''}`}
                                    >
                                        <td>{user.id}</td>
                                        <td
                                            className={`${styles.usernameCell} ${styles.clickable}`}
                                            onClick={() => navigateToUserDetails(user)}
                                        >
                                            {user.username}
                                            {user.is_current_user && <span className={styles.currentUserBadge}> (Ty)</span>}
                                        </td>
                                        <td className={styles.emailCell}>{user.email}</td>
                                        <td>
                                            {user.is_current_user ? (
                                                <div className={styles.roleText}>
                                                    {getRoleName(user.role)}
                                                    <span className={styles.tooltipText}>Nie możesz zmienić własnej roli</span>
                                                </div>
                                            ) : (
                                                <select
                                                    value={user.role}
                                                    onChange={(e) => changeUserRole(user.id, Number(e.target.value))}
                                                    className={styles.roleSelect}
                                                >
                                                    <option value={1}>Administrator</option>
                                                    <option value={2}>Moderator</option>
                                                    <option value={3}>Użytkownik</option>
                                                </select>
                                            )}
                                        </td>
                                        <td>
                                            <div className={user.is_active ? styles.activeStatus : styles.inactiveStatus}>
                                                {user.is_active ? 'Aktywny' : 'Nieaktywny'}
                                            </div>
                                        </td>
                                        <td>{formatDate(user.registration_date)}</td>
                                        <td>{formatDate(user.last_login)}</td>
                                        <td>
                                            {user.is_current_user ? (
                                                <div className={styles.disabledButtonWrapper}>
                                                    <button
                                                        className={`${styles.deactivateBtn} ${styles.disabledButton}`}
                                                        disabled={true}
                                                    >
                                                        Dezaktywuj
                                                    </button>
                                                    <span className={styles.tooltipText}>Nie możesz dezaktywować własnego konta</span>
                                                </div>
                                            ) : (
                                                <button
                                                    onClick={() => toggleUserStatus(user.id, user.is_active)}
                                                    className={user.is_active ? styles.deactivateBtn : styles.activateBtn}
                                                >
                                                    {user.is_active ? 'Dezaktywuj' : 'Aktywuj'}
                                                </button>
                                            )}
                                            <button
                                                onClick={() => navigateToUserDetails(user)}
                                                className={styles.detailsBtn}
                                            >
                                                Szczegóły
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {totalPages > 1 && (
                        <div className={styles.paginationContainer}>
                            <Pagination
                                currentPage={currentPage}
                                totalPages={totalPages}
                                onPageChange={handlePageChange}
                            />
                        </div>
                    )}

                    <div className={styles.userStats}>
                        <p>Łączna liczba użytkowników: <span className={styles.statValue}>{totalUsers}</span></p>
                    </div>
                </>
            )}
        </div>
    );
};

export default UserManagement;

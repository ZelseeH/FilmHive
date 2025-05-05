import React, { useEffect, useState } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { useGenres } from '../../hooks/useGenres';
import styles from './GenresPage.module.css';

interface Genre {
    id: number;
    name: string;
}

const PER_PAGE = 10;

const GenresPage: React.FC = () => {
    const { getToken } = useAuth();
    const token = getToken() || '';
    const { genres, loading, error, loadGenres, add, update, remove } = useGenres(token);

    const [searchQuery, setSearchQuery] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [showAddForm, setShowAddForm] = useState(false);
    const [newGenreName, setNewGenreName] = useState('');
    const [editingId, setEditingId] = useState<number | null>(null);
    const [editingName, setEditingName] = useState('');

    useEffect(() => {
        loadGenres();
    }, [loadGenres]);

    // Filtrowanie i paginacja
    const filteredGenres = genres.filter(g =>
        g.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
    const totalPages = Math.ceil(filteredGenres.length / PER_PAGE);
    const paginatedGenres = filteredGenres.slice((currentPage - 1) * PER_PAGE, currentPage * PER_PAGE);

    // Obsługa dodawania
    const handleAddGenre = (e: React.FormEvent) => {
        e.preventDefault();
        if (newGenreName.trim()) {
            add(newGenreName.trim());
            setNewGenreName('');
            setShowAddForm(false);
        }
    };

    // Obsługa edycji
    const handleEditGenre = (id: number, name: string) => {
        setEditingId(id);
        setEditingName(name);
    };
    const handleEditSave = (e: React.FormEvent) => {
        e.preventDefault();
        if (editingId !== null && editingName.trim()) {
            update(editingId, editingName.trim());
            setEditingId(null);
            setEditingName('');
        }
    };
    const handleEditCancel = () => {
        setEditingId(null);
        setEditingName('');
    };

    // Obsługa usuwania
    const handleDeleteGenre = (id: number) => {
        if (window.confirm('Na pewno usunąć gatunek?')) {
            remove(id);
        }
    };

    // Obsługa paginacji
    const handlePageChange = (page: number) => {
        setCurrentPage(page);
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Zarządzanie Gatunkami</h1>
                <p className={styles.description}>
                    Przeglądaj, wyszukuj i zarządzaj gatunkami muzycznymi w systemie.
                </p>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div className={styles.filtersContainer}>
                <form
                    onSubmit={e => { e.preventDefault(); setCurrentPage(1); }}
                    className={styles.searchForm}
                >
                    <input
                        type="text"
                        placeholder="Szukaj po nazwie gatunku..."
                        value={searchQuery}
                        onChange={e => { setSearchQuery(e.target.value); setCurrentPage(1); }}
                        className={styles.searchInput}
                    />
                    <button type="submit" className={styles.searchButton}>Szukaj</button>
                </form>
                <button
                    className={styles.addButton}
                    onClick={() => setShowAddForm(v => !v)}
                >
                    {showAddForm ? 'Anuluj' : '+ Dodaj gatunek'}
                </button>
            </div>

            {showAddForm && (
                <form onSubmit={handleAddGenre} className={styles.form}>
                    <input
                        className={styles.input}
                        type="text"
                        value={newGenreName}
                        onChange={e => setNewGenreName(e.target.value)}
                        placeholder="Nazwa nowego gatunku"
                        required
                        autoFocus
                    />
                    <div className={styles.buttonGroup}>
                        <button type="submit" className={styles.submitButton}>Dodaj</button>
                        <button
                            type="button"
                            className={styles.cancelButton}
                            onClick={() => { setShowAddForm(false); setNewGenreName(''); }}
                        >
                            Anuluj
                        </button>
                    </div>
                </form>
            )}

            {loading ? (
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Ładowanie gatunków...</p>
                </div>
            ) : (
                <div className={styles.tableContainer}>
                    <table className={styles.genresTable}>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nazwa</th>
                                <th>Akcje</th>
                            </tr>
                        </thead>
                        <tbody>
                            {paginatedGenres.length === 0 ? (
                                <tr>
                                    <td colSpan={3} className={styles.noData}>Brak wyników</td>
                                </tr>
                            ) : paginatedGenres.map(genre => (
                                <tr key={genre.id}>
                                    <td>{genre.id}</td>
                                    <td>
                                        {editingId === genre.id ? (
                                            <form onSubmit={handleEditSave} className={styles.inlineForm}>
                                                <input
                                                    className={styles.input}
                                                    type="text"
                                                    value={editingName}
                                                    onChange={e => setEditingName(e.target.value)}
                                                    required
                                                    autoFocus
                                                />
                                                <div className={styles.buttonGroup}>
                                                    <button type="submit" className={styles.submitButton}>Zapisz</button>
                                                    <button
                                                        type="button"
                                                        className={styles.cancelButton}
                                                        onClick={handleEditCancel}
                                                    >
                                                        Anuluj
                                                    </button>
                                                </div>
                                            </form>
                                        ) : (
                                            genre.name
                                        )}
                                    </td>
                                    <td>
                                        {editingId !== genre.id && (
                                            <>
                                                <button
                                                    className={styles.editButton}
                                                    onClick={() => handleEditGenre(genre.id, genre.name)}
                                                >
                                                    Edytuj
                                                </button>
                                                <button
                                                    className={styles.deleteButton}
                                                    onClick={() => handleDeleteGenre(genre.id)}
                                                >
                                                    Usuń
                                                </button>
                                            </>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {totalPages > 1 && (
                <div className={styles.paginationContainer}>
                    {Array.from({ length: totalPages }, (_, i) => (
                        <button
                            key={i + 1}
                            className={`${styles.pageButton} ${currentPage === i + 1 ? styles.activePage : ''}`}
                            onClick={() => handlePageChange(i + 1)}
                        >
                            {i + 1}
                        </button>
                    ))}
                </div>
            )}

            <div className={styles.genreStats}>
                <p>Łączna liczba gatunków: <span className={styles.statValue}>{filteredGenres.length}</span></p>
            </div>
        </div>
    );
};

export default GenresPage;

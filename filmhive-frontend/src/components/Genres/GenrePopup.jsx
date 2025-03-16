import React, { useState } from 'react';
import axios from 'axios';
import './genre.css'; // Używamy tych samych stylów

const GenrePopup = ({ genre, onClose, onEdit, onDelete }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [isConfirmingDelete, setIsConfirmingDelete] = useState(false); // Nowy stan dla potwierdzenia usunięcia
    const [newGenreName, setNewGenreName] = useState(genre.name);

    const handleEditGenre = async () => {
        if (!newGenreName.trim()) {
            alert('Nazwa gatunku nie może być pusta!');
            return;
        }

        try {
            const response = await axios.put(`http://localhost:5000/genres/${genre.id}`, {
                name: newGenreName,
            });
            onEdit(response.data); // Przekazujemy zaktualizowany gatunek do rodzica
        } catch (err) {
            alert('Nie udało się edytować gatunku.');
        }
    };

    const handleDeleteGenre = async () => {
        try {
            await axios.delete(`http://localhost:5000/genres/${genre.id}`);
            onDelete(genre.id); // Przekazujemy ID usuniętego gatunku do rodzica
        } catch (err) {
            alert('Nie udało się usunąć gatunku.');
        }
    };

    const startDeleteConfirmation = () => {
        setIsConfirmingDelete(true); // Przełączamy na tryb potwierdzenia usunięcia
    };

    const cancelDelete = () => {
        setIsConfirmingDelete(false); // Wracamy do widoku domyślnego
    };

    return (
        <>
            <div className="popup-overlay" onClick={onClose}></div>
            <div className="popup-container">
                {!isEditing && !isConfirmingDelete ? (
                    <>
                        <h2>{genre.name}</h2>
                        <button
                            onClick={() => setIsEditing(true)}
                            className="edit-btn"
                        >
                            Edytuj
                        </button>
                        <button
                            onClick={startDeleteConfirmation}
                            className="delete-btn"
                        >
                            Usuń
                        </button>
                        <button
                            onClick={onClose}
                            className="cancel-btn"
                        >
                            Anuluj
                        </button>
                    </>
                ) : isEditing ? (
                    <>
                        <h2>Edytuj Gatunek</h2>
                        <input
                            type="text"
                            value={newGenreName}
                            onChange={(e) => setNewGenreName(e.target.value)}
                        />
                        <button onClick={handleEditGenre} className="edit-btn">
                            Zapisz
                        </button>
                        <button onClick={onClose} className="cancel-btn">
                            Anuluj
                        </button>
                    </>
                ) : (
                    <>
                        <h2>Usuń Gatunek</h2>
                        <p className="delete-confirmation-text">
                            Czy na pewno chcesz usunąć gatunek "{genre.name}"?
                        </p>
                        <button onClick={handleDeleteGenre} className="delete-btn">
                            Tak, usuń
                        </button>
                        <button onClick={cancelDelete} className="cancel-btn">
                            Nie, anuluj
                        </button>
                    </>
                )}
            </div>
        </>
    );
};

export default GenrePopup;
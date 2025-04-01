import React, { useState } from 'react';
import axios from 'axios';
import './genre.css';

const AddGenrePopup = ({ onClose, onAdd }) => {
  const [genreName, setGenreName] = useState('');
  const [message, setMessage] = useState('');

  const handleAddGenre = async (e) => {
    e.preventDefault();
    if (!genreName.trim()) {
      setMessage('Nazwa gatunku jest wymagana!');
      return;
    }

    try {
      const response = await axios.post('http://localhost:5000/genres', { name: genreName });
      setMessage('Gatunek został dodany!');
      setGenreName('');
      onAdd(response.data);
      setTimeout(() => {
        onClose();
      }, 1000);
    } catch (err) {
      setMessage('Nie udało się dodać gatunku.');
    }
  };

  return (
    <>
      <div className="popup-overlay" onClick={onClose}></div>
      <div className="popup-container">
        <h2 className="add-genre-title">Dodaj Nowy Gatunek</h2>
        <form onSubmit={handleAddGenre} className="add-genre-form">
          <input
            type="text"
            placeholder="Wprowadź nazwę gatunku..."
            value={genreName}
            onChange={(e) => setGenreName(e.target.value)}
            className="add-genre-input"
          />
          <button type="submit" className="add-genre-btn">
            Dodaj Gatunek
          </button>
        </form>
        {message && <p className={`message ${message.includes('Nie udało') ? 'error' : 'success'}`}>{message}</p>}
        <button onClick={onClose} className="cancel-btn">
          Anuluj
        </button>
      </div>
    </>
  );
};

export default AddGenrePopup;
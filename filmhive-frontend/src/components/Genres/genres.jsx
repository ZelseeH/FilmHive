import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './genre.css';
import GenrePopup from './GenrePopup';
import AddGenrePopup from './AddGenrePopup'; // Nowy import

const Genres = () => {
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedGenre, setSelectedGenre] = useState(null);
  const [showAddPopup, setShowAddPopup] = useState(false); // Stan dla popupu dodawania

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await axios.get('http://localhost:5000/genres');
        setGenres(response.data);
        setLoading(false);
      } catch (err) {
        setError('Nie udało się pobrać danych.');
        setLoading(false);
      }
    };

    fetchGenres();
  }, []);

  const openPopup = (genre) => {
    setSelectedGenre(genre);
  };

  const closePopup = () => {
    setSelectedGenre(null);
  };

  const openAddPopup = () => {
    setShowAddPopup(true);
  };

  const closeAddPopup = () => {
    setShowAddPopup(false);
  };

  const handleAddGenre = (newGenre) => {
    setGenres([...genres, newGenre]); // Dodajemy nowy gatunek do listy
  };

  const handleEditGenre = (updatedGenre) => {
    setGenres(genres.map((genre) =>
      genre.id === updatedGenre.id ? updatedGenre : genre
    ));
    closePopup();
  };

  const handleDeleteGenre = (genreId) => {
    setGenres(genres.filter((genre) => genre.id !== genreId));
    closePopup();
  };

  if (loading) return <p>Ładowanie...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Gatunki Filmowe</h1>
      <button onClick={openAddPopup} className="add-genre-btn" position="center">
        Dodaj Gatunek
      </button>
      <div className="genres-container">
        {genres.map((genre) => (
          <div
            key={genre.id}
            onClick={() => openPopup(genre)}
            className="genre-item"
          >
            {genre.name}
          </div>
        ))}
      </div>

      {/* Popup do edycji/usuwania */}
      {selectedGenre && (
        <GenrePopup
          genre={selectedGenre}
          onClose={closePopup}
          onEdit={handleEditGenre}
          onDelete={handleDeleteGenre}
        />
      )}

      {/* Popup do dodawania */}
      {showAddPopup && (
        <AddGenrePopup
          onClose={closeAddPopup}
          onAdd={handleAddGenre}
        />
      )}
    </div>
  );
};

export default Genres;
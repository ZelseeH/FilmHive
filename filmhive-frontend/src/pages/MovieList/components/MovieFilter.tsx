// components/MovieFilter.tsx
import React, { useState } from 'react';
import styles from './MovieFilter.module.css';

interface Genre {
    id: number;
    name: string;
}

interface MovieFilterProps {
    genres: Genre[];
    selectedGenres: string[];
    onGenreToggle: (genre: string) => void;
}

const MovieFilter: React.FC<MovieFilterProps> = ({ genres, selectedGenres, onGenreToggle }) => {
    return (
        <div className={styles.filterContainer}>
            <h3>Gatunki</h3>
            <div className={styles.genreOptions}>
                {genres.map(genre => (
                    <button
                        key={genre.id}
                        className={`${styles.genreOption} ${selectedGenres.includes(genre.name) ? styles.selected : ''}`}
                        onClick={() => onGenreToggle(genre.name)}
                    >
                        {genre.name}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default MovieFilter;

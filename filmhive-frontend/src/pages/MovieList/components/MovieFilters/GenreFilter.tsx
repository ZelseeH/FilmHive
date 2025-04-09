import React, { useState } from 'react';
import styles from './GenreFilter.module.css';

interface Genre {
    id: number;
    name: string;
}

interface GenreFilterProps {
    genres: Genre[];
    selectedGenres: string[];
    isLoading: boolean;
    onToggle: (genreId: string) => void;
}

const GenreFilter: React.FC<GenreFilterProps> = ({
    genres,
    selectedGenres,
    isLoading,
    onToggle
}) => {
    const [showAll, setShowAll] = useState(false);
    const displayedGenres = showAll ? genres : genres.slice(0, 10);

    return (
        <div className={styles.filterSection}>
            <h3>Gatunki</h3>
            {isLoading ? (
                <div className={styles.loading}>Ładowanie gatunków...</div>
            ) : (
                <>
                    <div className={styles.genreList}>
                        {displayedGenres.map((genre) => (
                            <div
                                key={genre.id}
                                className={`${styles.genreItem} ${selectedGenres.includes(genre.id.toString()) ? styles.selected : ''}`}
                                onClick={() => onToggle(genre.id.toString())}
                            >
                                {genre.name}
                            </div>
                        ))}
                    </div>
                    {genres.length > 10 && (
                        <button
                            className={styles.showMoreButton}
                            onClick={() => setShowAll(!showAll)}
                        >
                            {showAll ? 'Pokaż mniej' : 'Pokaż wszystkie'}
                        </button>
                    )}
                </>
            )}
        </div>
    );
};

export default GenreFilter;

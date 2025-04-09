import React from 'react';
import styles from './MovieSorting.module.css';

interface SortOption {
    field: string;
    order: 'asc' | 'desc';
}

interface MovieSortingProps {
    value: SortOption;
    onChange: (newValue: SortOption) => void;
    onClose?: () => void;
}

const MovieSorting: React.FC<MovieSortingProps> = ({ value, onChange, onClose }) => {
    const handleSortChange = (field: string, order: 'asc' | 'desc') => {
        onChange({ field, order });
    };

    const isSelected = (field: string, order: 'asc' | 'desc') => {
        return value.field === field && value.order === order;
    };

    return (
        <div className={styles.sortingWrapper}>
            <div className={styles.sortingContainer}>
                <div className={styles.sortingHeader}>
                    <h2>SORTOWANIE</h2>
                    {onClose && (
                        <button onClick={onClose} className={styles.closeButton}>
                            ×
                        </button>
                    )}
                </div>

                <div className={styles.sortingContent}>
                    <div className={styles.sortingSection}>
                        <h3>Oceny:</h3>
                        <label className={styles.optionLabel}>
                            <span>najwyższe</span>
                            <input
                                type="radio"
                                checked={isSelected('average_rating', 'desc')}
                                onChange={() => handleSortChange('average_rating', 'desc')}
                            />
                        </label>
                        <label className={styles.optionLabel}>
                            <span>najniższe</span>
                            <input
                                type="radio"
                                checked={isSelected('average_rating', 'asc')}
                                onChange={() => handleSortChange('average_rating', 'asc')}
                            />
                        </label>
                    </div>

                    <div className={styles.sortingSection}>
                        <h3>Liczba ocen:</h3>
                        <label className={styles.optionLabel}>
                            <span>najwięcej</span>
                            <input
                                type="radio"
                                checked={isSelected('rating_count', 'desc')}
                                onChange={() => handleSortChange('rating_count', 'desc')}
                            />
                        </label>
                        <label className={styles.optionLabel}>
                            <span>najmniej</span>
                            <input
                                type="radio"
                                checked={isSelected('rating_count', 'asc')}
                                onChange={() => handleSortChange('rating_count', 'asc')}
                            />
                        </label>
                    </div>

                    <div className={styles.sortingSection}>
                        <h3>Rok produkcji:</h3>
                        <label className={styles.optionLabel}>
                            <span>najnowsze</span>
                            <input
                                type="radio"
                                checked={isSelected('year', 'desc')}
                                onChange={() => handleSortChange('year', 'desc')}
                            />
                        </label>
                        <label className={styles.optionLabel}>
                            <span>najstarsze</span>
                            <input
                                type="radio"
                                checked={isSelected('year', 'asc')}
                                onChange={() => handleSortChange('year', 'asc')}
                            />
                        </label>
                    </div>

                    <div className={styles.sortingSection}>
                        <h3>Tytuł:</h3>
                        <label className={styles.optionLabel}>
                            <span>A-Z</span>
                            <input
                                type="radio"
                                checked={isSelected('title', 'asc')}
                                onChange={() => handleSortChange('title', 'asc')}
                            />
                        </label>
                        <label className={styles.optionLabel}>
                            <span>Z-A</span>
                            <input
                                type="radio"
                                checked={isSelected('title', 'desc')}
                                onChange={() => handleSortChange('title', 'desc')}
                            />
                        </label>
                    </div>
                </div>

                {/* Przycisk zamykania w widoku mobilnym na dole */}
                {onClose && (
                    <div className={styles.closeButtonContainer}>
                        <button onClick={onClose} className={styles.closeButtonLarge}>
                            ×
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MovieSorting;
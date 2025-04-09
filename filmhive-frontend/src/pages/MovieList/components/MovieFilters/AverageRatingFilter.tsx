import React from 'react';
import styles from './AverageRatingFilter.module.css';

interface AverageRatingFilterProps {
    value: number;
    onChange: (value: number) => void;
}

const AverageRatingFilter: React.FC<AverageRatingFilterProps> = ({ value, onChange }) => {
    const ratings = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    const handleRatingClick = (rating: number) => {
        // If the same rating is clicked again, clear the selection
        if (value === rating) {
            onChange(0);
        } else {
            onChange(rating);
        }
    };

    return (
        <div className={styles.filterSection}>
            <h3>Średnia ocena</h3>
            <div className={styles.ratingButtons}>
                {ratings.map((rating) => (
                    <button
                        key={rating}
                        className={`${styles.ratingButton} ${value >= rating ? styles.selected : ''}`}
                        onClick={() => handleRatingClick(rating)}
                        aria-label={`Filtruj filmy z oceną ${rating} lub wyższą`}
                        aria-pressed={value >= rating}
                    >
                        {rating}
                    </button>
                ))}
            </div>
            {value > 0 && (
                <div className={styles.ratingInfo}>
                    Pokazuje filmy z oceną {value} lub wyższą
                </div>
            )}
        </div>
    );
};

export default AverageRatingFilter;

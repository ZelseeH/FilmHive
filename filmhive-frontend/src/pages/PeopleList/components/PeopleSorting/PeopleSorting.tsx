import React from 'react';
import styles from './PeopleSorting.module.css';

interface SortOption {
    field: string;
    order: 'asc' | 'desc';
}

interface PeopleSortingProps {
    value: SortOption;
    onChange: (newValue: SortOption) => void;
    onClose?: () => void;
    isDesktop?: boolean;
    // Możesz dodać props "personLabel" jeśli chcesz zmieniać nagłówek (np. "Imię i nazwisko aktora")
}

const PeopleSorting: React.FC<PeopleSortingProps> = ({ value, onChange, onClose, isDesktop }) => {
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
                    {onClose && !isDesktop && (
                        <button onClick={onClose} className={styles.closeButton}>
                            ×
                        </button>
                    )}
                </div>

                <div className={styles.sortingContent}>
                    <div className={styles.sortingSection}>
                        <h3>Imię i nazwisko:</h3>
                        <label className={styles.optionLabel}>
                            <span>A-Z</span>
                            <input
                                type="radio"
                                checked={isSelected('name', 'asc')}
                                onChange={() => handleSortChange('name', 'asc')}
                            />
                        </label>
                        <label className={styles.optionLabel}>
                            <span>Z-A</span>
                            <input
                                type="radio"
                                checked={isSelected('name', 'desc')}
                                onChange={() => handleSortChange('name', 'desc')}
                            />
                        </label>
                    </div>

                    <div className={styles.sortingSection}>
                        <h3>Data urodzenia:</h3>
                        <label className={styles.optionLabel}>
                            <span>najstarsi</span>
                            <input
                                type="radio"
                                checked={isSelected('birth_date', 'asc')}
                                onChange={() => handleSortChange('birth_date', 'asc')}
                            />
                        </label>
                        <label className={styles.optionLabel}>
                            <span>najmłodsi</span>
                            <input
                                type="radio"
                                checked={isSelected('birth_date', 'desc')}
                                onChange={() => handleSortChange('birth_date', 'desc')}
                            />
                        </label>
                    </div>
                </div>

                {onClose && !isDesktop && (
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

export default PeopleSorting;

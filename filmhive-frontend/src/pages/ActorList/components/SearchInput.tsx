import React from 'react';
import styles from './SearchInput.module.css';

interface SearchInputProps {
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onClear: () => void;
    onSubmit: (e: React.FormEvent) => void;
}

const SearchInput: React.FC<SearchInputProps> = ({ value, onChange, onClear, onSubmit }) => {
    return (
        <form onSubmit={onSubmit} className={styles.searchForm}>
            <div className={styles.inputWrapper}>
                <input
                    type="text"
                    placeholder="Szukaj aktora..."
                    value={value}
                    onChange={onChange}
                    className={styles.searchInput}
                />
                {value && (
                    <button
                        type="button"
                        className={styles.clearButton}
                        onClick={onClear}
                        aria-label="Wyczyść"
                    >
                        ×
                    </button>
                )}
            </div>

        </form>
    );
};

export default SearchInput;

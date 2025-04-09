import React from 'react';
import styles from './SearchInput.module.css';

interface SearchInputProps {
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onClear: () => void;
    onSubmit: (e: React.FormEvent) => void;
    placeholder?: string;
}

const SearchInput: React.FC<SearchInputProps> = ({
    value,
    onChange,
    onClear,
    onSubmit,
    placeholder = "Szukaj..."
}) => {
    return (
        <form className={styles.searchForm} onSubmit={onSubmit}>
            <div className={styles.searchInputContainer}>
                <input
                    type="text"
                    className={styles.searchInput}
                    value={value}
                    onChange={onChange}
                    placeholder={placeholder}
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

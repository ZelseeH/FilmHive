import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaSearch } from "react-icons/fa";
import styles from "./SearchBar.module.css";

const SearchBar: React.FC = () => {
    const [search, setSearch] = useState("");
    const navigate = useNavigate();

    const handleSubmit = (e?: React.FormEvent | React.MouseEvent) => {
        if (e) e.preventDefault();
        if (search.trim()) {
            navigate(`/search?query=${encodeURIComponent(search.trim())}`);
            setSearch("");
        }
    };

    return (
        <form className={styles["search-container"]} onSubmit={handleSubmit} role="search" autoComplete="off">
            <input
                type="text"
                className={styles["search-input"]}
                placeholder="Szukaj filmów, osób, użytkowników..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                aria-label="Szukaj"
            />
            <button
                type="submit"
                className={styles["search-button"]}
                aria-label="Szukaj"
            >
                <FaSearch />
            </button>
        </form>
    );
};

export default SearchBar;

import React from 'react';
import styles from './Pagination.module.css';

interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({ currentPage, totalPages, onPageChange }) => {
    if (totalPages <= 1) return null;

    const renderPageNumbers = () => {
        const pageNumbers = [];

        pageNumbers.push(
            <button
                key={1}
                onClick={() => onPageChange(1)}
                className={`${styles.paginationButton} ${currentPage === 1 ? styles.active : ''}`}
            >
                1
            </button>
        );

        if (currentPage > 3) {
            pageNumbers.push(
                <span key="ellipsis1" className={styles.paginationEllipsis}>...</span>
            );
        }

        for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
            if (i === 1 || i === totalPages) continue;

            pageNumbers.push(
                <button
                    key={i}
                    onClick={() => onPageChange(i)}
                    className={`${styles.paginationButton} ${currentPage === i ? styles.active : ''}`}
                >
                    {i}
                </button>
            );
        }
        if (currentPage < totalPages - 2) {
            pageNumbers.push(
                <span key="ellipsis2" className={styles.paginationEllipsis}>...</span>
            );
        }
        if (totalPages > 1) {
            pageNumbers.push(
                <button
                    key={totalPages}
                    onClick={() => onPageChange(totalPages)}
                    className={`${styles.paginationButton} ${currentPage === totalPages ? styles.active : ''}`}
                >
                    {totalPages}
                </button>
            );
        }

        return pageNumbers;
    };

    return (
        <div className={styles.pagination}>
            <button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={styles.paginationButton}
                aria-label="Poprzednia strona"
            >
                &lt;
            </button>
            {renderPageNumbers()}
            <button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={styles.paginationButton}
                aria-label="Następna strona"
            >
                &gt;
            </button>
        </div>
    );
};


export default Pagination;

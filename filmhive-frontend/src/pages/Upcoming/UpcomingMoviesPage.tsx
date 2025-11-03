import React, { useState } from 'react';
import { useUpcomingMovies } from './hooks/useUpcomingMovies';
import UpcomingMovieItem from './components/UpcomingMovieItem/UpcomingMovieItem';
import styles from './UpcomingMoviesPage.module.css';

const UpcomingMoviesPage: React.FC = () => {
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth() + 1;

    const [selectedYear, setSelectedYear] = useState<number>(currentYear);
    const [selectedMonth, setSelectedMonth] = useState<number>(currentMonth);

    const { movies, loading, error, monthName, totalCount } = useUpcomingMovies(selectedYear, selectedMonth);

    const years = Array.from({ length: 4 }, (_, i) => currentYear + i);

    const months = [
        { number: 1, name: 'Styczeń' },
        { number: 2, name: 'Luty' },
        { number: 3, name: 'Marzec' },
        { number: 4, name: 'Kwiecień' },
        { number: 5, name: 'Maj' },
        { number: 6, name: 'Czerwiec' },
        { number: 7, name: 'Lipiec' },
        { number: 8, name: 'Sierpień' },
        { number: 9, name: 'Wrzesień' },
        { number: 10, name: 'Październik' },
        { number: 11, name: 'Listopad' },
        { number: 12, name: 'Grudzień' }
    ];

    const handleYearChange = (year: number) => {
        setSelectedYear(year);
    };

    const handleMonthChange = (month: number) => {
        setSelectedMonth(month);
    };

    return (
        <div className={styles.upcomingMoviesPage}>
            <div className={styles.backgroundElements}>
                <div className={styles.gradientOrb1}></div>
                <div className={styles.gradientOrb2}></div>
                <div className={styles.gradientOrb3}></div>
            </div>

            <div className={styles.pageContainer}>
                <div className={styles.header}>
                    <h1>Nadchodzące Premiery</h1>

                </div>

                <div className={styles.selectorContainer}>
                    <div className={styles.yearSelector}>
                        <h3 className={styles.selectorTitle}>Wybierz rok</h3>
                        <div className={styles.buttonGroup}>
                            {years.map(year => (
                                <button
                                    key={year}
                                    className={`${styles.yearButton} ${selectedYear === year ? styles.active : ''}`}
                                    onClick={() => handleYearChange(year)}
                                >
                                    {year}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className={styles.monthSelector}>
                        <h3 className={styles.selectorTitle}>Wybierz miesiąc</h3>
                        <div className={styles.monthGrid}>
                            {months.map(month => (
                                <button
                                    key={month.number}
                                    className={`${styles.monthButton} ${selectedMonth === month.number ? styles.active : ''}`}
                                    onClick={() => handleMonthChange(month.number)}
                                >
                                    {month.name}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className={styles.selectedPeriod}>
                    <div className={styles.periodHeader}>
                        <h2>Premiery w {monthName} {selectedYear}</h2>
                        {movies.length > 0 && (
                            <div className={styles.movieCount}>
                                <span className={styles.countNumber}>{totalCount}</span>
                                <span className={styles.countLabel}>
                                    {totalCount === 1 ? 'film' : 'filmów'}
                                </span>
                            </div>
                        )}
                    </div>
                </div>

                <div className={styles.moviesContainer}>
                    {loading ? (
                        <div className={styles.loading}>
                            <div className={styles.loadingSpinner}></div>
                            <span>Ładowanie nadchodzących premier...</span>
                        </div>
                    ) : error ? (
                        <div className={styles.error}>
                            <div className={styles.errorIcon}>⚠️</div>
                            <span>Błąd: {error}</span>
                        </div>
                    ) : movies.length > 0 ? (
                        <div className={styles.moviesList}>
                            {movies.map((movie, index) => (
                                <div
                                    key={movie.id || movie.movie_id}
                                    className={styles.movieItemWrapper}
                                    style={{ animationDelay: `${index * 0.1}s` }}
                                >
                                    <UpcomingMovieItem movie={movie} />
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className={styles.noMovies}>
                            <div className={styles.noMoviesIcon}>🎭</div>
                            <h3>Brak nadchodzących premier</h3>
                            <p>W {monthName} {selectedYear} nie ma zaplanowanych premier filmowych.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default UpcomingMoviesPage;

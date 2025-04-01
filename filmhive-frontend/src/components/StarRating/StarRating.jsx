import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './StarRating.module.css';

const StarRating = ({ movieId, onRatingChange }) => {
    const { user, getToken, openLoginModal } = useAuth();
    const [rating, setRating] = useState(0);
    const [hover, setHover] = useState(0);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const fetchingRef = useRef(false);
    useEffect(() => {
        const fetchUserRating = async () => {
            if (!user || !movieId || fetchingRef.current) {
                console.log(`Pomijam pobieranie: user=${!!user}, movieId=${movieId}, fetchingRef=${fetchingRef.current}`);
                return;
            }

            console.log(`Rozpoczynam pobieranie oceny dla filmu ${movieId}`);
            fetchingRef.current = true;
            setIsLoading(true);

            try {
                const token = getToken();
                if (!token) {
                    console.log('Brak dostępnego tokenu, przerywam pobieranie');
                    setIsLoading(false);
                    fetchingRef.current = false;
                    return;
                }

                console.log(`Pobieranie oceny dla filmu ${movieId} z tokenem`);
                const response = await fetch(`http://localhost:5000/api/ratings/movies/${movieId}/user-rating`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Cache-Control': 'no-cache, no-store, must-revalidate'
                    }
                });

                console.log(`Status odpowiedzi: ${response.status}`);

                if (!response.ok) {
                    throw new Error(`Nie udało się pobrać oceny: ${response.status}`);
                }

                const data = await response.json();
                console.log('Otrzymane dane:', data);

                let ratingValue = 0;

                if (data && typeof data === 'object') {
                    if (data.rating !== undefined && !isNaN(Number(data.rating))) {
                        ratingValue = Number(data.rating);
                    } else if (data.id && data.rating !== undefined && !isNaN(Number(data.rating))) {
                        ratingValue = Number(data.rating);
                    }
                }

                console.log(`Ustawiam ocenę na ${ratingValue}`);
                setRating(ratingValue);

                if (onRatingChange && ratingValue > 0) {
                    onRatingChange(ratingValue);
                }
            } catch (error) {
                console.error('Błąd podczas pobierania oceny użytkownika:', error);
                setError('Nie udało się pobrać oceny');
            } finally {
                console.log('Pobieranie zakończone');
                setIsLoading(false);
                fetchingRef.current = false;
            }
        };

        fetchUserRating();

        return () => {
            console.log('Czyszczenie: ustawiam fetchingRef na false');
            fetchingRef.current = false;
        };
    }, [user, movieId]);

    const handleRatingClick = async (selectedRating) => {
        if (!user) {
            console.log('Użytkownik niezalogowany, otwieram modal logowania');
            openLoginModal();
            return;
        }

        if (isSubmitting) {
            console.log('Wysyłanie oceny już w toku, pomijam');
            return;
        }

        console.log(`Wysyłam ocenę ${selectedRating} dla filmu ${movieId}`);
        setIsSubmitting(true);
        setError(null);

        try {
            const token = getToken();
            if (!token) {
                throw new Error('Musisz być zalogowany, aby ocenić film');
            }

            console.log('Wysyłam żądanie POST, aby ocenić film');
            const response = await fetch(`http://localhost:5000/api/ratings/movies/${movieId}/ratings`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ rating: selectedRating })
            });

            console.log(`Status odpowiedzi: ${response.status}`);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Wystąpił błąd podczas oceniania filmu');
            }

            const data = await response.json();
            console.log('Ocena wysłana pomyślnie:', data);

            console.log(`Ustawiam ocenę na ${selectedRating}`);
            setRating(selectedRating);
            if (onRatingChange) {
                onRatingChange(selectedRating);
            }
        } catch (err) {
            console.error('Błąd podczas wysyłania oceny:', err);
            setError(err.message);
        } finally {
            console.log('Wysyłanie oceny zakończone');
            setIsSubmitting(false);
        }
    };

    const safeRating = !isNaN(rating) ? rating : 0;

    return (
        <div className={styles['rating-container']}>

            <div className={styles['stars-container']}>
                {[...Array(10)].map((_, index) => {
                    const ratingValue = index + 1;
                    const isFilled = ratingValue <= (hover || safeRating);
                    return (
                        <span
                            key={index}
                            className={`${styles.star} ${isFilled ? styles.filled : ''}`}
                            onClick={() => handleRatingClick(ratingValue)}
                            onMouseEnter={() => setHover(ratingValue)}
                            onMouseLeave={() => setHover(0)}
                        >
                            ★
                        </span>
                    );
                })}
            </div>

            {safeRating > 0 && <div className={styles['current-rating']}>Twoja ocena: {safeRating}/10</div>}
            {isLoading && <div className={styles['loading']}>Ładowanie oceny...</div>}
            {isSubmitting && <div className={styles['loading']}>Zapisywanie oceny...</div>}
            {error && <div className={styles['error']}>{error}</div>}
            {!user && <div className={styles['login-prompt']}>Zaloguj się, aby ocenić film</div>}
        </div>
    );
};

export default StarRating;

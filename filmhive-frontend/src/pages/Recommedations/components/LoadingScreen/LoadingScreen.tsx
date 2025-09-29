import React, { useState, useEffect } from 'react';
import styles from './LoadingScreen.module.css';

interface LoadingScreenProps {
    message?: string;
    subMessage?: string;
    duration?: number; // Dodajemy kontrolę czasu trwania
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({
    message = 'Generuję rekomendacje...',
    subMessage = 'To może potrwać chwilę...',
    duration = 8000 // Domyślnie 8 sekund (jak w RecommendationsPage)
}) => {
    const [dots, setDots] = useState('');
    const [progress, setProgress] = useState(0);
    const [currentMessage, setCurrentMessage] = useState(0);

    const loadingMessages = [
        'Analizuję Twoje preferencje...',
        'Przeglądam bazę filmów...',
        'Obliczam podobieństwa...',
        'Tworzę spersonalizowane rekomendacje...',
        'Prawie gotowe...'
    ];

    useEffect(() => {
        // Animacja kropek - co 500ms
        const dotsInterval = setInterval(() => {
            setDots(prev => prev.length >= 3 ? '' : prev + '.');
        }, 500);

        // Progress bar zsynchronizowany z czasem ładowania
        const progressInterval = setInterval(() => {
            setProgress(prev => {
                const increment = (100 / duration) * 100; // Increment na 100ms
                const newProgress = prev + increment;
                return newProgress >= 100 ? 100 : newProgress;
            });
        }, 100); // Co 100ms

        // Zmiana wiadomości co 2 sekundy lub na podstawie progresu
        const messageInterval = setInterval(() => {
            setCurrentMessage(prev => {
                const nextMessage = (prev + 1) % loadingMessages.length;
                return nextMessage;
            });
        }, duration / loadingMessages.length); // Równo rozłożone na czas trwania

        return () => {
            clearInterval(dotsInterval);
            clearInterval(progressInterval);
            clearInterval(messageInterval);
        };
    }, [duration]);

    // Aktualizuj wiadomość na podstawie progresu
    useEffect(() => {
        const messageIndex = Math.min(
            Math.floor((progress / 100) * loadingMessages.length),
            loadingMessages.length - 1
        );
        setCurrentMessage(messageIndex);
    }, [progress]);

    return (
        <div className={styles.loadingScreen}>
            <div className={styles.loadingContainer}>
                <div className={styles.movieReels}>
                    <div className={styles.reel}></div>
                    <div className={styles.reel}></div>
                    <div className={styles.reel}></div>
                </div>

                <h2 className={styles.mainMessage}>
                    {message}{dots}
                </h2>

                <p className={styles.subMessage}>
                    {loadingMessages[currentMessage]}
                </p>

                <div className={styles.progressBar}>
                    <div
                        className={styles.progressFill}
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>



                <p className={styles.tipMessage}>
                    {subMessage}
                </p>
            </div>
        </div>
    );
};

export default LoadingScreen;

// src/pages/ActorDetails/ActorDetails.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import styles from './ActorDetails.module.css';
import { useActorDetails } from './hooks/useActorDetails';
import ActorHeaderSection from './components/ActorHeaderSection/ActorHeaderSection';
import ActorFilmography from './components/ActorFilmography/ActorFilmography';
import { getActorMovies } from './services/actorService';
import { ActorMovie } from './services/actorService';

interface LocationState {
    actorId?: number;
}

const ActorDetail: React.FC = () => {
    const { actorName } = useParams<{ actorName: string }>();
    const { state } = useLocation();
    const locationState = state as LocationState | undefined;
    const actorId = locationState?.actorId;

    const [showFullBio, setShowFullBio] = useState<boolean>(false);
    const [movies, setMovies] = useState<ActorMovie[]>([]);
    const [loadingMovies, setLoadingMovies] = useState<boolean>(false);

    const { actor, loading, error } = useActorDetails(actorId, actorName);


    useEffect(() => {
        if (actor?.id) {
            setLoadingMovies(true);
            getActorMovies(actor.id)
                .then((data) => {
                    console.log('API response:', data);
                    console.log('Movies with roles:', data.movies);
                    setMovies(data.movies);
                    setLoadingMovies(false);
                })
                .catch((err) => {
                    console.error('Błąd podczas pobierania filmów aktora:', err);
                    setLoadingMovies(false);
                });
        }
    }, [actor?.id]);

    useEffect(() => {
        if (actor?.id) {
            setLoadingMovies(true);
            getActorMovies(actor.id)
                .then((data: { movies: ActorMovie[] }) => {
                    setMovies(data.movies);
                    setLoadingMovies(false);
                })
                .catch((err: Error) => {
                    console.error('Błąd podczas pobierania filmów aktora:', err);
                    setLoadingMovies(false);
                });
        }
    }, [actor?.id]);

    const toggleBioModal = () => {
        setShowFullBio((prev) => !prev);
    };

    if (loading) return <div className={styles['loading']}>Ładowanie szczegółów aktora...</div>;
    if (error) return <div className={styles['error']}>Błąd: {error}</div>;
    if (!actor) return <div className={styles['not-found']}>Aktor nie został znaleziony</div>;

    return (
        <div className={styles['actor-detail-container']}>
            <ActorHeaderSection actor={actor} onShowFullBio={toggleBioModal} />

            {loadingMovies ? (
                <div className={styles['loading']}>Ładowanie filmografii...</div>
            ) : (
                <ActorFilmography movies={movies} />
            )}

            {showFullBio && (
                <div
                    className={styles['modal-backdrop']}
                    onClick={toggleBioModal}
                    role="dialog"
                    aria-labelledby="modal-title"
                >
                    <div className={styles['modal-content']} onClick={(e) => e.stopPropagation()}>
                        <button
                            className={styles['modal-close-btn']}
                            onClick={toggleBioModal}
                            aria-label="Zamknij biografię"
                        >
                            ×
                        </button>
                        <h2 id="modal-title">{actor.name} - Pełna biografia</h2>
                        <p>{actor.biography || 'Brak dostępnej biografii.'}</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ActorDetail;

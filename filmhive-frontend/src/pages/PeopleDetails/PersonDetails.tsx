import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import styles from './PersonDetails.module.css';
import { usePersonDetails } from './hooks/usePersonDetails';
import PersonHeaderSection from './components/PersonHeaderSection/PersonHeaderSection';
import PersonFilmography from './components/PersonFilmography/PersonFilmography';
import { getPersonMovies, PersonMovie } from './services/peopleService';

interface LocationState {
    personId?: number;
    personType?: 'actor' | 'director';
}

const PersonDetails: React.FC = () => {
    const { personType, personName } = useParams<{ personType: 'actor' | 'director', personName: string }>();
    const { state } = useLocation();
    const locationState = state as LocationState | undefined;
    const personId = locationState?.personId;
    const type = personType || locationState?.personType || 'actor';

    // Debug logs
    console.log('PersonDetails:', { personType, personName, locationState, personId, type });

    const [showFullBio, setShowFullBio] = useState<boolean>(false);
    const [movies, setMovies] = useState<PersonMovie[]>([]);
    const [loadingMovies, setLoadingMovies] = useState<boolean>(false);

    const { person, loading, error } = usePersonDetails(personId, personName, type);

    useEffect(() => {
        if (person?.id) {
            console.log(`Fetching movies for person id=${person.id}, type=${person.type}`);
            setLoadingMovies(true);
            getPersonMovies(person.id, person.type, 1, 'all', 'release_date', 'desc')
                .then((data) => {
                    console.log('API response movies:', data);
                    setMovies(data.movies);
                    setLoadingMovies(false);
                })
                .catch((err) => {
                    console.error(`Błąd podczas pobierania filmów ${person.type === 'actor' ? 'aktora' : 'reżysera'}:`, err);
                    setLoadingMovies(false);
                });
        }
    }, [person?.id, person?.type]);

    const toggleBioModal = () => {
        setShowFullBio(prev => !prev);
    };

    if (loading) return <div className={styles['loading']}>Ładowanie szczegółów...</div>;
    if (error) return <div className={styles['error']}>Błąd: {error}</div>;
    if (!person) return <div className={styles['not-found']}>Nie znaleziono osoby</div>;

    return (
        <div className={styles['person-detail-container']}>
            <PersonHeaderSection person={person} onShowFullBio={toggleBioModal} />

            {loadingMovies ? (
                <div className={styles['loading']}>Ładowanie filmografii...</div>
            ) : (
                <PersonFilmography
                    personId={person.id}
                    personType={person.type}
                    initialMovies={movies}
                />
            )}

            {showFullBio && (
                <div
                    className={styles['modal-backdrop']}
                    onClick={toggleBioModal}
                    role="dialog"
                    aria-labelledby="modal-title"
                >
                    <div className={styles['modal-content']} onClick={e => e.stopPropagation()}>
                        <button
                            className={styles['modal-close-btn']}
                            onClick={toggleBioModal}
                            aria-label="Zamknij biografię"
                        >
                            ×
                        </button>
                        <h2 id="modal-title">{person.name} - Pełna biografia</h2>
                        <p>{person.biography || 'Brak dostępnej biografii.'}</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PersonDetails;

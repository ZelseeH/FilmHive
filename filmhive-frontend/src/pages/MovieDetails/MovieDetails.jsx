import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import styles from './MovieDetails.module.css';
import { useAuth } from '../../contexts/AuthContext';
import StarRating from '../../components/StarRating/StarRating';
import MovieHeaderSection from '../../components/MovieDetailsComp/MovieHeaderSection';
import MovieCastSection from '../../components/MovieDetailsComp/MovieCastSection';

const YouTubeTrailer = ({ url }) => {
    const getEmbedUrl = (youtubeUrl) => {
        if (!youtubeUrl) return null;
        let videoId;
        if (youtubeUrl.includes('youtube.com/watch')) {
            const urlParams = new URLSearchParams(new URL(youtubeUrl).search);
            videoId = urlParams.get('v');
        } else if (youtubeUrl.includes('youtu.be')) {
            videoId = youtubeUrl.split('/').pop();
        } else if (youtubeUrl.includes('youtube.com/embed')) {
            videoId = youtubeUrl.split('/').pop();
        }
        return videoId ? `https://www.youtube.com/embed/${videoId}` : null;
    };

    const embedUrl = getEmbedUrl(url);

    if (!embedUrl) {
        return <div className={styles['no-trailer']}>Brak dostępnego trailera</div>;
    }

    return (
        <div className={styles['responsive-embed']}>
            <iframe
                width="560"
                height="315"
                src={embedUrl}
                title="YouTube trailer"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
            ></iframe>
        </div>
    );
};

const MovieDetail = () => {
    const { movieTitle } = useParams();
    const location = useLocation();
    const movieId = location.state?.movieId;
    const { user } = useAuth(); // Usunięto getToken, bo nie jest już potrzebne
    const [movie, setMovie] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showFullDescription, setShowFullDescription] = useState(false);
    const [userRating, setUserRating] = useState(0);

    useEffect(() => {
        const fetchMovieDetails = async () => {
            try {
                setLoading(true);
                let response;
                if (movieId) {
                    response = await fetch(`http://localhost:5000/api/movies/${movieId}?include_roles=true`);
                } else {
                    const allMoviesResponse = await fetch('http://localhost:5000/api/movies/all');
                    const allMovies = await allMoviesResponse.json();
                    const createSlug = (title) => title.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').replace(/--+/g, '-');
                    const foundMovie = allMovies.find(m => createSlug(m.title) === movieTitle);
                    if (foundMovie) {
                        response = await fetch(`http://localhost:5000/api/movies/${foundMovie.id}?include_roles=true`);
                    } else {
                        throw new Error('Film nie został znaleziony');
                    }
                }
                if (!response.ok) {
                    throw new Error('Nie udało się pobrać szczegółów filmu');
                }
                const data = await response.json();
                setMovie(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchMovieDetails();
    }, [movieTitle, movieId]);

    // Usunięto useEffect do pobierania oceny użytkownika

    if (loading) return <div className={styles['loading']}>Ładowanie szczegółów filmu...</div>;
    if (error) return <div className={styles['error']}>Błąd: {error}</div>;
    if (!movie) return <div className={styles['not-found']}>Film nie został znaleziony</div>;


    return (
        <div className={styles['movie-detail-container']}>
            <MovieHeaderSection
                movie={movie}
                onShowFullDescription={() => setShowFullDescription(true)}
                onRatingChange={(newRating) => setUserRating(newRating)}
            />

            {/* Modal z pełnym opisem */}
            {showFullDescription && (
                <div className={styles['modal-backdrop']} onClick={() => setShowFullDescription(false)}>
                    <div className={styles['modal-content']} onClick={e => e.stopPropagation()}>
                        <button
                            className={styles['modal-close-btn']}
                            onClick={() => setShowFullDescription(false)}
                        >
                            ×
                        </button>
                        <h2>{movie.title} - Pełny opis</h2>
                        <p>{movie.description}</p>
                    </div>
                </div>
            )}

            {movie.trailer_url && (
                <section className={styles['trailer-section']}>
                    <h2 className={styles['section-title']}>Zwiastun</h2>
                    <YouTubeTrailer url={movie.trailer_url} />
                </section>
            )}

            {movie.actors && movie.actors.length > 0 && (
                <MovieCastSection actors={movie.actors} />
            )}
        </div>
    );
};

export default MovieDetail;
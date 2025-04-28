import React, { useRef, useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { RecentRatedMovie } from "../../services/userMoviesService";
import { createSlug } from "../../../../utils/formatters";
import styles from "./RecentRatedMovies.module.css";
import StarRating from "../../../MovieDetails/components/StarRating/StarRating";
import CommentSection from "../../../MovieDetails/components/CommentSection/CommentSection";

function useOutsideClick(ref: React.RefObject<HTMLDivElement | null>, callback: () => void) {
    useEffect(() => {
        function handleClick(event: MouseEvent) {
            if (ref.current && !ref.current.contains(event.target as Node)) {
                callback();
            }
        }
        document.addEventListener("mousedown", handleClick);
        return () => {
            document.removeEventListener("mousedown", handleClick);
        };
    }, [ref, callback]);
}

function useIsMobile(breakpoint = 500) {
    const [isMobile, setIsMobile] = useState(window.innerWidth < breakpoint);

    useEffect(() => {
        const onResize = () => setIsMobile(window.innerWidth < breakpoint);
        window.addEventListener("resize", onResize);
        return () => window.removeEventListener("resize", onResize);
    }, [breakpoint]);

    return isMobile;
}

interface Props {
    movies: RecentRatedMovie[];
    loading: boolean;
    error: string | null;
}

const POPUP_WIDTH = 320;
const POPUP_MARGIN = 8;

const RecentRatedMovies: React.FC<Props> = ({ movies, loading, error }) => {
    const [activeMovieId, setActiveMovieId] = useState<number | null>(null);
    const [popupPosition, setPopupPosition] = useState<{ left: number; top: number } | null>(null);
    const popupRef = useRef<HTMLDivElement | null>(null);
    const badgeRefs = useRef<{ [key: number]: HTMLSpanElement | null }>({});
    const isMobile = useIsMobile(500);

    useEffect(() => {
        if (isMobile && activeMovieId !== null) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }
        return () => {
            document.body.style.overflow = "";
        };
    }, [isMobile, activeMovieId]);

    useOutsideClick(
        popupRef,
        () => {
            if (activeMovieId !== null && !isMobile) {
                setActiveMovieId(null);
                setPopupPosition(null);
            }
        }
    );


    const updatePopupPosition = useCallback(() => {
        if (activeMovieId !== null && !isMobile) {
            const badge = badgeRefs.current[activeMovieId];
            if (badge) {
                const badgeRect = badge.getBoundingClientRect();
                let left = badgeRect.left;
                if (left + POPUP_WIDTH + POPUP_MARGIN > window.innerWidth) {
                    left = window.innerWidth - POPUP_WIDTH - POPUP_MARGIN;
                }
                if (left < POPUP_MARGIN) {
                    left = POPUP_MARGIN;
                }
                const top = badgeRect.bottom;
                setPopupPosition({ left, top });
            }
        }
    }, [activeMovieId, isMobile]);


    useEffect(() => {
        if (activeMovieId !== null && !isMobile) {
            updatePopupPosition();
            window.addEventListener("scroll", updatePopupPosition);
            window.addEventListener("resize", updatePopupPosition);
            return () => {
                window.removeEventListener("scroll", updatePopupPosition);
                window.removeEventListener("resize", updatePopupPosition);
            };
        }
    }, [activeMovieId, isMobile, updatePopupPosition]);

    const handleBadgeClick = (e: React.MouseEvent, movieId: number) => {
        e.preventDefault();
        setActiveMovieId(movieId);
        setTimeout(() => {
            updatePopupPosition();
        }, 0);
    };

    const closePopup = () => {
        setActiveMovieId(null);
        setPopupPosition(null);
    };

    if (loading) return <div>Ładowanie ocenionych filmów...</div>;
    if (error) return <div>Błąd: {error}</div>;
    if (!movies.length) return <div>Brak ocenionych filmów.</div>;

    return (
        <div className={styles.container}>
            <h3>Ostatnio ocenione filmy</h3>
            <div className={styles.moviesList}>
                {movies.map((movie) => (
                    <div key={movie.movie_id} className={styles.movieCardWrapper}>
                        <Link
                            to={`/movie/details/${createSlug(movie.title)}`}
                            state={{ movieId: movie.movie_id }}
                            className={styles.movieCard}
                            tabIndex={0}
                        >
                            <div className={styles.posterWrapper}>
                                <img
                                    src={movie.poster_url || "/default-poster.jpg"}
                                    alt={movie.title}
                                    className={styles.poster}
                                    draggable={false}
                                />
                                <span
                                    className={styles.ratingBadge}
                                    ref={el => { badgeRefs.current[movie.movie_id] = el; }}
                                    onClick={e => handleBadgeClick(e, movie.movie_id)}
                                    tabIndex={0}
                                    role="button"
                                    aria-label={`Oceń film ${movie.title}`}
                                >
                                    <span className={styles.star}>★</span>
                                    <span className={styles.ratingValue}>{movie.rating}</span>
                                </span>
                            </div>
                            <div className={styles.title}>{movie.title}</div>
                        </Link>

                        {activeMovieId === movie.movie_id && (
                            isMobile ? (
                                <div
                                    className={styles.popupBackdropMobile}
                                    onClick={closePopup}
                                >
                                    <div
                                        className={`${styles.ratingPopup} ${styles.ratingPopupMobile}`}
                                        ref={popupRef}
                                        onClick={e => e.stopPropagation()}
                                    >
                                        <div className={styles.ratingPopupContent}>
                                            <h4>Twoja ocena filmu {movie.title}</h4>
                                            <StarRating movieId={movie.movie_id} />
                                            <CommentSection key={movie.movie_id} movieId={movie.movie_id} />
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div
                                    className={styles.ratingPopup}
                                    ref={popupRef}
                                    style={{
                                        zIndex: 999,
                                        position: "fixed",
                                        left: popupPosition?.left ?? 0,
                                        top: popupPosition?.top ?? 0,
                                    }}
                                >
                                    <div className={styles.ratingPopupContent}>
                                        <h4>Twoja ocena filmu {movie.title}</h4>
                                        <StarRating movieId={movie.movie_id} />
                                        <CommentSection key={movie.movie_id} movieId={movie.movie_id} />
                                    </div>
                                </div>
                            )
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RecentRatedMovies;

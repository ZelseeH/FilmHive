import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Actor } from '../../services/movieService';
import { handleImageError } from '../../utils/movieUtils';
import styles from './MovieCastSection.module.css';
import { useSlider } from '../../hooks/useSlider';
import { createSlug } from '../../../../utils/formatters';

interface MovieCastSectionProps {
    actors: Actor[];
    title?: string;
}

const MovieCastSection: React.FC<MovieCastSectionProps> = ({ actors, title }) => {
    const { sliderRef, scrollLeft, scrollRight } = useSlider(200);
    const [canScrollLeft, setCanScrollLeft] = useState(false);
    const [canScrollRight, setCanScrollRight] = useState(false);
    const [showArrows, setShowArrows] = useState(false);

    useEffect(() => {
        const checkScrollability = () => {
            if (sliderRef.current) {
                const element = sliderRef.current;
                const { scrollWidth, clientWidth, scrollLeft: currentScrollLeft } = element;

                const needsScrolling = scrollWidth > clientWidth;
                setShowArrows(needsScrolling);

                if (needsScrolling) {
                    const canScrollL = currentScrollLeft > 0;
                    const canScrollR = currentScrollLeft < scrollWidth - clientWidth - 1;

                    setCanScrollLeft(canScrollL);
                    setCanScrollRight(canScrollR);
                } else {
                    setCanScrollLeft(false);
                    setCanScrollRight(false);
                }
            }
        };

        const timeoutId = setTimeout(checkScrollability, 100);

        if (sliderRef.current) {
            const element = sliderRef.current;
            element.addEventListener('scroll', checkScrollability);
            window.addEventListener('resize', checkScrollability);

            return () => {
                clearTimeout(timeoutId);
                element.removeEventListener('scroll', checkScrollability);
                window.removeEventListener('resize', checkScrollability);
            };
        }

        return () => clearTimeout(timeoutId);
    }, [actors, sliderRef]);

    if (!actors || actors.length === 0) return null;

    return (
        <section className={styles['cast-section']}>
            <h2 className={styles['section-title']}>
                {title || 'Obsada filmu'}
            </h2>
            <div className={styles['cast-slider-container']}>
                {showArrows && canScrollLeft && (
                    <button
                        className={`${styles['slider-arrow']} ${styles['left-arrow']}`}
                        onClick={scrollLeft}
                        aria-label="Scroll left"
                        type="button"
                    >
                        ❮
                    </button>
                )}

                <div className={styles['cast-slider-wrapper']}>
                    <div
                        className={`${styles['cast-slider']} ${!showArrows ? styles['centered'] : ''}`}
                        ref={sliderRef}
                    >
                        {actors.map(actor => (
                            <Link
                                to={`/people/actor/${createSlug(actor.name)}`}
                                state={{ personId: actor.id }}
                                className={styles['cast-member']}
                                key={actor.id}
                            >
                                <div className={styles['actor-photo']}>
                                    {actor.photo_url ? (
                                        <img
                                            src={actor.photo_url}
                                            alt={actor.name}
                                            onError={(e) => handleImageError(e, '/placeholder-actor.jpg')}
                                            loading="lazy"
                                        />
                                    ) : (
                                        <div className={styles['no-poster']}>Brak zdjęcia</div>
                                    )}
                                </div>
                                <div className={styles['actor-name']}>{actor.name}</div>
                                {actor.role && <div className={styles['actor-role']}>{actor.role}</div>}
                            </Link>
                        ))}
                    </div>
                </div>

                {showArrows && canScrollRight && (
                    <button
                        className={`${styles['slider-arrow']} ${styles['right-arrow']}`}
                        onClick={scrollRight}
                        aria-label="Scroll right"
                        type="button"
                    >
                        ❯
                    </button>
                )}
            </div>
        </section>
    );
};

export default MovieCastSection;

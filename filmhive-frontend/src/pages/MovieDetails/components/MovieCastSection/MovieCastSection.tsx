// src/components/MovieCastSection/MovieCastSection.tsx
import React from 'react';
import { Actor } from '../../services/movieService';
import { handleImageError } from '../../utils/movieUtils';
import styles from './MovieCastSection.module.css';
import { useSlider } from '../../hooks/useSlider';

interface MovieCastSectionProps {
    actors: Actor[];
    title?: string;
}

const MovieCastSection: React.FC<MovieCastSectionProps> = ({ actors, title }) => {
    const { sliderRef, scrollLeft, scrollRight } = useSlider(200);

    if (!actors || actors.length === 0) return null;

    return (
        <section className={styles['cast-section']}>
            <h2 className={styles['section-title']}>
                {title || 'Obsada filmu'}
            </h2>
            <div className={styles['cast-slider-container']}>
                <div className={styles['cast-slider-wrapper']}>
                    <div className={styles['cast-slider']} ref={sliderRef}>
                        {actors.map(actor => (
                            <div key={actor.id} className={styles['cast-member']}>
                                <div className={styles['actor-photo']}>
                                    {actor.photo_url ? (
                                        <img
                                            src={actor.photo_url}
                                            alt={actor.name}
                                            onError={(e) => handleImageError(e, '/placeholder-actor.jpg')}
                                        />
                                    ) : (
                                        <div className={styles['no-poster']}>Brak zdjęcia</div>
                                    )}
                                </div>
                                <div className={styles['actor-name']}>{actor.name}</div>
                                {actor.role && <div className={styles['actor-role']}>{actor.role}</div>}
                            </div>
                        ))}
                    </div>
                    <div className={`${styles['slider-arrow']} ${styles['left-arrow']}`} onClick={scrollLeft}>❮</div>
                    <div className={`${styles['slider-arrow']} ${styles['right-arrow']}`} onClick={scrollRight}>❯</div>
                </div>
            </div>
        </section >
    );
};

export default MovieCastSection;

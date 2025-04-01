import React, { useRef } from 'react';
import styles from './MovieCastSection.module.css';

const MovieCastSection = ({ actors, title }) => {
    const sliderRef = useRef(null);

    if (!actors || actors.length === 0) return null;

    const scrollLeft = () => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: -200, behavior: 'smooth' });
        }
    };

    const scrollRight = () => {
        if (sliderRef.current) {
            sliderRef.current.scrollBy({ left: 200, behavior: 'smooth' });
        }
    };

    return (
        <section className={styles['cast-section']}>
            <h2 className={styles['section-title']}>
                {title || 'Obsada filmu'} <span className={styles['arrow-icon']}>›</span>
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
                                            onError={(e) => {
                                                e.target.onerror = null;
                                                e.target.src = '/placeholder-actor.jpg';
                                            }}
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
        </section>
    );
};

export default MovieCastSection;
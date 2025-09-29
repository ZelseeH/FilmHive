import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Person } from '../../services/peopleService';
import {
  getPersonSlug,
  handlePersonImageError,
  getPersonInitials,
  formatPersonBirthDate,
  calculateAge,
} from '../../utils/personUtils';
import styles from './BirthdayActors.module.css';
import { useSlider } from '../../hooks/useslider';

interface BirthdayActorsProps {
  people: Person[];
  title?: string;
}

const BirthdayActors: React.FC<BirthdayActorsProps> = ({ people, title }) => {
  const { sliderRef, scrollLeft, scrollRight } = useSlider(160);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [showArrows, setShowArrows] = useState(false);

  // Sprawdzenie czy potrzebne są przyciski scroll - PRZED return
  useEffect(() => {
    const checkScrollability = () => {
      if (sliderRef.current) {
        const element = sliderRef.current;
        const { scrollWidth, clientWidth, scrollLeft: currentScrollLeft } = element;

        // Sprawdź czy w ogóle potrzebne są strzałki
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

    // Sprawdź po renderze z małym opóźnieniem
    const timeoutId = setTimeout(checkScrollability, 100);

    if (sliderRef.current) {
      const element = sliderRef.current;
      element.addEventListener('scroll', checkScrollability);

      // Check on resize
      window.addEventListener('resize', checkScrollability);

      return () => {
        clearTimeout(timeoutId);
        element.removeEventListener('scroll', checkScrollability);
        window.removeEventListener('resize', checkScrollability);
      };
    }

    return () => clearTimeout(timeoutId);
  }, [people, sliderRef]);

  // Warunkowy return DOPIERO PO wszystkich hookach
  if (!people || people.length === 0) return null;

  return (
    <section className={styles['birthday-section']}>
      <h2 className={styles['section-title']}>{title || 'Dzisiaj obchodzą urodziny'}</h2>

      <div className={styles['slider-container']}>
        {/* Pokazuj strzałki tylko gdy są potrzebne */}
        {showArrows && canScrollLeft && (
          <button
            className={`${styles['arrow']} ${styles['left-arrow']}`}
            onClick={scrollLeft}
            aria-label="Scroll left"
            type="button"
          >
            ❮
          </button>
        )}

        <div className={styles['slider-wrapper']}>
          <div
            className={`${styles['slider']} ${!showArrows ? styles['centered'] : ''}`}
            ref={sliderRef}
          >
            {people.map((person) => {
              const age = calculateAge(person.birth_date);

              return (
                <Link
                  to={`/people/${person.type}/${getPersonSlug(person.name)}`}
                  state={{ personId: person.id, personType: person.type }}
                  key={`${person.type}-${person.id}`}
                  className={styles['slider-item']}
                >
                  <div className={styles['photo-container']}>
                    {person.photo_url ? (
                      <img
                        src={person.photo_url}
                        alt={person.name}
                        onError={(e) => handlePersonImageError(e, person.type)}
                        loading="lazy"
                      />
                    ) : (
                      <div className={styles['no-photo']}>{getPersonInitials(person.name)}</div>
                    )}
                  </div>
                  <div className={styles['person-name']}>{person.name}</div>
                  {person.birth_date && (
                    <div className={styles['birth-info']}>
                      {formatPersonBirthDate(person.birth_date)} {age !== null && `(${age} lat)`}
                    </div>
                  )}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Pokazuj strzałki tylko gdy są potrzebne */}
        {showArrows && canScrollRight && (
          <button
            className={`${styles['arrow']} ${styles['right-arrow']}`}
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

export default BirthdayActors;

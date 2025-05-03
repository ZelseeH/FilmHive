import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Footer.module.css';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className={styles.footer}>
      <div className={styles.footerContainer}>
        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>FilmHive</h3>
          <p className={styles.footerDescription}>
            Twoja społeczność filmowa, gdzie możesz odkrywać, oceniać i dyskutować o filmach z całego świata.
          </p>

        </div>

        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>Odkrywaj</h3>
          <ul className={styles.footerLinks}>
            <li><Link to="/movies">Filmy</Link></li>
            <li><Link to="/movies?sort_by=average_rating&sort_order=desc">Najwyżej oceniane</Link></li>
            <li><Link to="/upcoming">Nadchodzące premiery</Link></li>
          </ul>
        </div>

        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>Informacje</h3>
          <ul className={styles.footerLinks}>
            <li><Link to="/about">O nas</Link></li>
            <li><Link to="/contact">Kontakt</Link></li>
          </ul>
        </div>

        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>Dokumenty prawne</h3>
          <ul className={styles.footerLinks}>
            <li><Link to="/terms">Regulamin</Link></li>
            <li><Link to="/privacy">Polityka prywatności</Link></li>
          </ul>
        </div>
      </div>

      <div className={styles.footerBottom}>
        <p className={styles.copyright}>
          &copy; {currentYear} FilmHive. Wszystkie prawa zastrzeżone.
        </p>
      </div>
    </footer>
  );
};

export default Footer;

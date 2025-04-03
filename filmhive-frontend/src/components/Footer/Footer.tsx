// src/components/Footer/Footer.tsx
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
          <div className={styles.socialLinks}>
            <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
              <i className="fab fa-facebook-f"></i>
            </a>
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
              <i className="fab fa-twitter"></i>
            </a>
            <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
              <i className="fab fa-instagram"></i>
            </a>
          </div>
        </div>

        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>Odkrywaj</h3>
          <ul className={styles.footerLinks}>
            <li><Link to="/movies">Filmy</Link></li>
            <li><Link to="/top-rated">Najwyżej oceniane</Link></li>
            <li><Link to="/upcoming">Nadchodzące premiery</Link></li>
            <li><Link to="/genres">Gatunki</Link></li>
          </ul>
        </div>

        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>Informacje</h3>
          <ul className={styles.footerLinks}>
            <li><Link to="/about">O nas</Link></li>
            <li><Link to="/contact">Kontakt</Link></li>
            <li><Link to="/faq">FAQ</Link></li>
            <li><Link to="/support">Wsparcie</Link></li>
          </ul>
        </div>

        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>Dokumenty prawne</h3>
          <ul className={styles.footerLinks}>
            <li><Link to="/terms">Regulamin</Link></li>
            <li><Link to="/privacy">Polityka prywatności</Link></li>
            <li><Link to="/cookies">Polityka cookies</Link></li>
            <li><Link to="/gdpr">RODO</Link></li>
          </ul>
        </div>
      </div>

      <div className={styles.footerBottom}>
        <p className={styles.copyright}>
          &copy; {currentYear} FilmHive. Wszystkie prawa zastrzeżone.
        </p>
        <p className={styles.attribution}>
          Dane filmowe dostarczane przez <a href="https://www.themoviedb.org" target="_blank" rel="noopener noreferrer">TMDB</a>
        </p>
      </div>
    </footer>
  );
};

export default Footer;

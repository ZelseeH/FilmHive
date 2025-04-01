import React from "react";
import styles from "./Footer.module.css"; // Zmiana importu na moduł CSS

const Footer = () => {
  return (
    <footer className={styles.footer}> {/* Użycie styles.footer zamiast "footer" */}
      <p>© {new Date().getFullYear()} FilmHive. Wszelkie prawa zastrzeżone.</p>
    </footer>
  );
};

export default Footer;
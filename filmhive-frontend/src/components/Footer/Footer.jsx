import React from "react";
import styles from "./Footer.module.css";

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <p>© {new Date().getFullYear()} FilmHive. Wszelkie prawa zastrzeżone.</p>
    </footer>
  );
};

export default Footer;
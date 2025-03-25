import React from "react";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <p>© {new Date().getFullYear()} FilmHive. Wszelkie prawa zastrzeżone.</p>
    </footer>
  );
};

export default Footer;

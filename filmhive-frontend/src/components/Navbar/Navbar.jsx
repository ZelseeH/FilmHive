import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './Navbar.module.css';
import logo from './FilmHiveLogo.png';
import LoginModal from '../LoginModal/LoginModal';
import { useAuth } from '../../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const { user, logout, isLoginModalOpen, openLoginModal, closeLoginModal } = useAuth();
  const userMenuRef = useRef(null);
  const userSectionRef = useRef(null);
  const [show, setShow] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  const toggleMenu = () => {
    setIsOpen(prev => !prev);
  };

  const toggleUserMenu = () => {
    setIsUserMenuOpen(prev => !prev);
  };

  const handleLogout = () => {
    setIsUserMenuOpen(false);
    logout();

    const currentPath = window.location.pathname;
    if (currentPath === '/profile' || currentPath.startsWith('/profile/') || currentPath === '/settings') {
      window.location.href = '/';
    } else {
      navigate('/');
    }
  };

  const controlNavbar = () => {
    const isMobile = window.innerWidth <= 992;
    const currentScrollY = window.scrollY;

    if (isMobile) {
      if (currentScrollY > lastScrollY && currentScrollY > 60) {
        setShow(false);
        setIsOpen(false); // Zamykamy menu hamburgera, gdy navbar się chowa
      } else {
        setShow(true);
      }
      setLastScrollY(currentScrollY);
    } else {
      setShow(true);
      setIsOpen(false); // Zamykamy menu na desktopie, jeśli było otwarte
    }
  };

  useEffect(() => {
    window.addEventListener('scroll', controlNavbar);

    return () => {
      window.removeEventListener('scroll', controlNavbar);
    };
  }, [lastScrollY]);

  useEffect(() => {
    const updateUserMenuPosition = () => {
      if (isUserMenuOpen && userMenuRef.current && userSectionRef.current) {
        const userSectionRect = userSectionRef.current.getBoundingClientRect();
        const windowWidth = window.innerWidth;
        const isMobile = windowWidth <= 1100;

        if (isMobile) {
          userMenuRef.current.style.right = '0px';
          userMenuRef.current.style.left = 'auto';
        } else {
          const rightOffset = windowWidth - userSectionRect.right;
          userMenuRef.current.style.right = `${rightOffset}px`;
          userMenuRef.current.style.left = 'auto';
        }
      }
    };

    updateUserMenuPosition();
    window.addEventListener('resize', updateUserMenuPosition);

    const handleClickOutside = (event) => {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target) &&
        !userSectionRef.current.contains(event.target)
      ) {
        setIsUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      window.removeEventListener('resize', updateUserMenuPosition);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isUserMenuOpen]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 1100 && isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [isOpen]);

  const menuVariants = {
    open: {
      opacity: 1,
      height: 'auto',
      y: 0,
      transition: {
        duration: 0.3,
        ease: 'easeOut',
        when: 'beforeChildren',
        staggerChildren: 0.1,
      },
    },
    closed: {
      opacity: 0,
      height: 0,
      y: -10,
      transition: {
        duration: 0.3,
        ease: 'easeIn',
        when: 'afterChildren',
      },
    },
  };

  const childVariants = {
    open: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.2,
        ease: 'easeOut',
      },
    },
    closed: {
      opacity: 0,
      y: 10,
      transition: {
        duration: 0.2,
        ease: 'easeIn',
      },
    },
  };

  const UserAvatar = ({ user }) => (
    <div className={styles['user-avatar']} onClick={toggleUserMenu}>
      {user.avatar ? (
        <img src={user.avatar} alt={user.username} />
      ) : (
        <div className={styles['user-initial']}>{user.username[0].toUpperCase()}</div>
      )}
    </div>
  );

  const UserMenu = () => (
    <motion.div
      className={styles['user-menu']}
      ref={userMenuRef}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      <Link to={`/profile/${user.username}`} className={styles['user-menu-item']} onClick={() => setIsUserMenuOpen(false)}>
        Mój Profil
      </Link>
      <Link to="/settings" className={styles['user-menu-item']} onClick={() => setIsUserMenuOpen(false)}>
        Ustawienia
      </Link>
      <button className={`${styles['user-menu-item']} ${styles['logout-btn']}`} onClick={handleLogout}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          viewBox="0 0 16 16"
          className={styles['logout-icon']}
        >
          <path
            fillRule="evenodd"
            d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"
          />
          <path
            fillRule="evenodd"
            d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"
          />
        </svg>
        <span className={styles['logout-text']}>Wyloguj</span>
      </button>
    </motion.div>
  );

  return (
    <div className={`${styles['navbar-container']} ${show ? '' : styles.hidden}`}>
      <nav className={`${styles.navbar} ${show ? '' : styles.hidden}`}>
        <div className={styles['navbar-logo']}>
          <Link to="/">
            <img src={logo} alt="FilmHive Logo" />
          </Link>
        </div>

        <div className={`${styles['navbar-links']} ${styles['desktop-links']}`}>
          <div className={styles['search-container']}>
            <div className={styles['search-icon']}>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z" />
              </svg>
            </div>
            <input type="text" placeholder="Szukaj na FilmHive" className={styles['search-input']} />
          </div>
          <Link to="/movies" className={styles['movies-link']}>
            Filmy
          </Link>
        </div>

        <div className={styles['user-section']} ref={userSectionRef}>
          {user ? (
            <div className={styles['user-info']}>
              <span className={styles.username}>{user.username}</span>
              <UserAvatar user={user} />
            </div>
          ) : (
            <button className={styles['login-btn']} onClick={openLoginModal}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                viewBox="0 0 16 16"
                className={styles['login-icon']}
              >
                <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z" />
              </svg>
              Zaloguj się
            </button>
          )}
        </div>

        <div className={`${styles.hamburger} ${isOpen ? styles.open : ''}`} onClick={toggleMenu}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </nav>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className={styles['mobile-links']}
            initial="closed"
            animate="open"
            exit="closed"
            variants={menuVariants}
          >
            <motion.div className={styles['search-container']} variants={childVariants}>
              <div className={styles['search-icon']}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z" />
                </svg>
              </div>
              <input type="text" placeholder="Szukaj na FilmHive" className={styles['search-input']} />
            </motion.div>
            <motion.div variants={childVariants}>
              <Link to="/movies" className={styles['movies-link']}>
                Filmy
              </Link>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isUserMenuOpen && user && <UserMenu />}
      </AnimatePresence>

      <LoginModal isOpen={isLoginModalOpen} onClose={closeLoginModal} />
    </div>
  );
};

export default Navbar;
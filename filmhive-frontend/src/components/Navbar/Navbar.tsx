import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { slide as Menu } from 'react-burger-menu';
import Hamburger from 'hamburger-react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavbarVisibility } from '../../hooks/useNavbarVisibility';
import { useUserMenu } from '../../hooks/useUserMenu';
import { useMobileMenu } from '../../hooks/useMobileMenu';
import { handleLogout } from '../../services/navbarService';
import logo from './FilmHiveLogo.png';

import SearchBar from './SearchBar/SearchBar';
import LoginModal from '../LoginModal/LoginModal';
import UserMenu from './UserMenu/UserMenu';
import styles from './Navbar.module.css';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout, isLoginModalOpen, openLoginModal, closeLoginModal } = useAuth();
  const { show } = useNavbarVisibility();
  const { mobileMenuOpen, toggleMobileMenu, closeMobileMenu } = useMobileMenu();
  const { showUserMenu, menuPosition, avatarRef, toggleUserMenu, closeUserMenu } = useUserMenu();

  const onLogout = () => handleLogout(logout, closeUserMenu, navigate);

  return (
    <div className={`${styles['navbar-container']} ${show ? '' : styles.hidden}`}>
      <nav className={`${styles.navbar} ${show ? '' : styles.hidden}`}>
        <div className={styles['navbar-logo']}>
          <Link to="/">
            <img src={logo} alt="FilmHive Logo" />
          </Link>
        </div>

        <div className={`${styles['navbar-links']} ${styles['desktop-links']}`}>
          <SearchBar />
          <Link to="/movies" className={styles['movies-link']}>
            Filmy
          </Link>
        </div>

        <div className={styles['user-section']}>
          {user ? (
            <div className={styles['user-info']}>
              <span className={styles.username}>{user.username}</span>

              <div
                id="user-avatar"
                ref={avatarRef}
                onClick={toggleUserMenu}
                className={styles['user-avatar']}
              >
                {user.username[0].toUpperCase()}
              </div>
            </div>
          ) : (
            <button className={styles['login-btn']} onClick={openLoginModal}>
              Zaloguj się
            </button>
          )}
        </div>

        <div className={styles['hamburger-container']}>
          <Hamburger
            toggled={mobileMenuOpen}
            toggle={toggleMobileMenu}
            color="#ffffff"
            size={24}
            duration={0.3}
            distance="sm"
            rounded
          />
        </div>
      </nav>

      <Menu
        right
        isOpen={mobileMenuOpen}
        onClose={closeMobileMenu}
        width={'280px'}
        customBurgerIcon={false}
        customCrossIcon={false}
        className={styles.burgerMenu}
        overlayClassName={styles.burgerOverlay}
      >
        <div className={styles.mobileMenuContent}>
          <SearchBar />
          <Link to="/movies" className={styles['mobile-menu-link']} onClick={closeMobileMenu}>
            Filmy
          </Link>
        </div>
      </Menu>

      {showUserMenu && user && (
        <UserMenu
          username={user.username}
          onClose={closeUserMenu}
          onLogout={onLogout}
          position={menuPosition}
        />
      )}

      <LoginModal isOpen={isLoginModalOpen} onClose={closeLoginModal} />
    </div>
  );
};

export default Navbar;

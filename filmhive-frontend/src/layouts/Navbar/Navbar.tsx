import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { slide as Menu } from 'react-burger-menu';
import Hamburger from 'hamburger-react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavbarVisibility } from './hooks/useNavbarVisibility';
import { useUserMenu } from './hooks/useUserMenu';
import { useMobileMenu } from './hooks/useMobileMenu';
import { handleLogout } from './services/navbarService';
import logo from './FilmHiveLogo.png';

import SearchBar from './SearchBar/SearchBar';
import LoginModal from '../../components/LoginModal/LoginModal';
import UserMenu from './UserMenu/UserMenu';
import UserAvatar from './UserAvatar/UserAvatar';
import styles from './Navbar.module.css';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout, isLoginModalOpen, openLoginModal, closeLoginModal } = useAuth();
  const { show } = useNavbarVisibility();
  const { mobileMenuOpen, toggleMobileMenu, closeMobileMenu } = useMobileMenu();
  const { showUserMenu, menuPosition, avatarRef, toggleUserMenu, closeUserMenu } = useUserMenu();

  const onLogout = () => handleLogout(logout, closeUserMenu, navigate);

  useEffect(() => {
    const preventTouchMove = (e: TouchEvent) => {
      e.preventDefault();
    };

    if (mobileMenuOpen) {
      document.body.classList.add('menu-open');
      document.documentElement.classList.add('menu-open');
      document.addEventListener('touchmove', preventTouchMove, { passive: false });
      document.body.style.overflow = 'hidden';
      document.documentElement.style.overflow = 'hidden';
    } else {
      document.body.classList.remove('menu-open');
      document.documentElement.classList.remove('menu-open');
      document.removeEventListener('touchmove', preventTouchMove);
      document.body.style.overflow = '';
      document.documentElement.style.overflow = '';
    }

    return () => {
      document.body.classList.remove('menu-open');
      document.documentElement.classList.remove('menu-open');
      document.removeEventListener('touchmove', preventTouchMove);
      document.body.style.overflow = '';
      document.documentElement.style.overflow = '';
    };
  }, [mobileMenuOpen]);

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
          <div className={styles['topnav-right']}>
            <Link to="/movies" className={styles['movies-link']}>
              Filmy
            </Link>
            <Link to="/actors" className={styles['movies-link']}>
              Aktorzy
            </Link>
          </div>
        </div>

        <div className={styles['user-section']}>
          {user ? (
            <div className={styles['user-info']}>
              <span className={styles.username}>{user.username}</span>
              <div ref={avatarRef} id="user-avatar">
                <UserAvatar
                  user={{
                    username: user.username,
                    profile_picture: user.profile_picture,
                  }}
                  onClick={toggleUserMenu}
                />
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
          <div className={styles.mobileMenuLinks}>
            <SearchBar />
            <Link to="/movies" className={styles['mobile-menu-link']} onClick={closeMobileMenu}>
              Filmy
            </Link>
            <Link to="/actors" className={styles['mobile-menu-link']} onClick={closeMobileMenu}>
              Aktorzy
            </Link>
          </div>
          <div className={styles.spacer}></div> {/* Pusty element wypełniający przestrzeń */}
          <div className={styles.mobileUserSection}>
            {user ? (
              <>
                <div className={styles.mobileUserProfile}>
                  <div className={styles.mobileUserAvatar}>
                    <UserAvatar
                      user={{
                        username: user.username,
                        profile_picture: user.profile_picture,
                      }}
                      onClick={() => { }}
                    />
                  </div>
                  <span className={styles.mobileUsername}>{user.username}</span>
                </div>
                <Link
                  to={`/profile/${user.username}`}
                  className={styles['mobile-menu-link']}
                  onClick={closeMobileMenu}
                >
                  Mój Profil
                </Link>
                <Link
                  to="/settings"
                  className={styles['mobile-menu-link']}
                  onClick={closeMobileMenu}
                >
                  Ustawienia
                </Link>
                <button
                  className={styles['mobile-logout-btn']}
                  onClick={() => {
                    onLogout();
                    closeMobileMenu();
                  }}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    fill="currentColor"
                    viewBox="0 0 16 16"
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
                  <span>Wyloguj</span>
                </button>
              </>
            ) : (
              <button
                className={styles.mobileLoginBtn}
                onClick={() => {
                  closeMobileMenu();
                  openLoginModal();
                }}
              >
                Zaloguj się
              </button>
            )}
          </div>
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
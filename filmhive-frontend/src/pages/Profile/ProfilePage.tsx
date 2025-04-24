import React from 'react';
import { useParams } from 'react-router-dom';
import ProfileHeader from './components/ProfileHeader/ProfileHeader';
import { useProfileData } from './hooks/useProfileData';
import { useRecentRatedMovies } from './hooks/useRecentRatedMovies';
import { useRecentFavoriteMovies } from './hooks/useRecentFavoriteMovies';
import { useRecentWatchlistMovies } from './hooks/useRecentWatchlistMovies';
import RecentRatedMovies from './components/RecentRatedMovies/RecentRatedMovies';
import RecentFavoriteMovies from './components/RecentFavoriteMovies/RecentFavoriteMovies';
import RecentWatchlistMovies from './components/RecentWatchlistMovies/RecentWatchlistMovies';
import styles from './ProfilePage.module.css';

const ProfilePage: React.FC = () => {
  const { username } = useParams<{ username?: string }>();
  const { profileData, loading, error, isOwnProfile, refreshProfile } = useProfileData(username);

  const { movies: recentRatedMovies, loading: ratingsLoading, error: ratingsError } = useRecentRatedMovies(username);
  const {
    movies: recentFavoriteMovies,
    loading: favoritesLoading,
    error: favoritesError,
    removeLoading: removeFavoriteLoading,
    removeFavorite
  } = useRecentFavoriteMovies(username);
  const {
    movies: recentWatchlistMovies,
    loading: watchlistLoading,
    error: watchlistError,
    removeLoading: removeWatchlistLoading,
    removeFromWatchlist
  } = useRecentWatchlistMovies(username);

  if (loading) {
    return <div className={`${styles['profile-page']} ${styles.loading}`}>Ładowanie profilu...</div>;
  }

  if (error) {
    return <div className={`${styles['profile-page']} ${styles.error}`}>Błąd: {error}</div>;
  }

  if (!profileData) {
    return <div className={`${styles['profile-page']} ${styles.error}`}>Nie znaleziono profilu</div>;
  }

  return (
    <div className={styles['profile-page']}>
      <ProfileHeader
        profileData={profileData}
        isOwnProfile={isOwnProfile}
        onBioUpdate={refreshProfile}
        onImageUpdate={refreshProfile}
      />

      <div className={styles['profile-content']}>
        <div className={styles['profile-section']}>
          <h2>Aktywność</h2>
          <RecentRatedMovies
            movies={recentRatedMovies}
            loading={ratingsLoading}
            error={ratingsError}
          />
          <RecentFavoriteMovies
            movies={recentFavoriteMovies}
            loading={favoritesLoading}
            error={favoritesError}
            isOwnProfile={isOwnProfile}
            onFavoriteRemoved={removeFavorite}
            removeLoading={removeFavoriteLoading}
          />
          <RecentWatchlistMovies
            movies={recentWatchlistMovies}
            loading={watchlistLoading}
            error={watchlistError}
            isOwnProfile={isOwnProfile}
            onWatchlistRemoved={removeFromWatchlist}
            removeLoading={removeWatchlistLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;

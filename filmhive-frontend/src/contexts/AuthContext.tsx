import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';

// Interfejs zgodny z backendem Marshmallow
export interface User {
  user_id: number;
  username: string;
  email: string;
  name?: string;
  bio?: string;
  profile_picture?: string;
  registration_date?: string;
  background_image?: string;
  background_position?: { x: number; y: number };
  role?: number;
  // Dodaj inne pola jeśli są potrzebne
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (userData: User, token: string) => void;
  logout: () => void;
  isLoginModalOpen: boolean;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [loading, setLoading] = useState<boolean>(true);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState<boolean>(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
  }, [user]);

  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;

    const verifyTokenInBackground = async (): Promise<void> => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch('http://localhost:5000/api/user/profile', {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` },
          signal
        });

        if (!response.ok) {
          if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setUser(null);
          }
        } else {
          // Jeśli backend zwraca { user: {...} }
          // const { user } = await response.json();
          // setUser(user);

          // Jeśli backend zwraca bezpośrednio usera:
          const userData = await response.json();
          setUser(userData);
        }
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          console.error('Error verifying token:', error);
        }
      } finally {
        setLoading(false);
      }
    };

    verifyTokenInBackground();
    return () => controller.abort();
  }, []);

  const login = (userData: User, token: string): void => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    closeLoginModal();
<<<<<<< Updated upstream

    navigate('/');
=======
    window.location.href = '/';
>>>>>>> Stashed changes
  };

  const logout = (): void => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
<<<<<<< Updated upstream

    if (window.location.pathname !== '/') {
      navigate('/');
    }
=======
    window.location.href = '/';
>>>>>>> Stashed changes
  };

  const openLoginModal = (): void => {
    setIsLoginModalOpen(true);
  };

  const closeLoginModal = (): void => {
    setIsLoginModalOpen(false);
  };

  const getToken = (): string | null => {
    return localStorage.getItem('token');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isLoginModalOpen,
        openLoginModal,
        closeLoginModal,
        getToken
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;

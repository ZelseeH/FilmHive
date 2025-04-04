import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';

// Definiujemy typy
interface User {
  // Dodaj odpowiednie pola użytkownika
  [key: string]: any;
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

// Tworzymy kontekst z domyślnymi wartościami
const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Inicjalizujemy stan użytkownika z localStorage
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [loading, setLoading] = useState<boolean>(true);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState<boolean>(false);
  const navigate = useNavigate();

  // Synchronizujemy stan użytkownika z localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
  }, [user]);

  // Weryfikujemy token w tle, ale nie blokujemy renderowania
  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;

    const verifyTokenInBackground = async (): Promise<void> => {
      console.log("Verifying token in background...");
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
            console.error("Token validation failed");
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setUser(null);
          }
        } else {
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

    // Uruchamiamy weryfikację tokenu, ale nie blokujemy renderowania
    verifyTokenInBackground();

    return () => controller.abort();
  }, []);

  const login = (userData: User, token: string): void => {
    console.log("Login function called with:", { userData, tokenExists: !!token });
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData)); // Zapisujemy użytkownika do localStorage
    setUser(userData);
    closeLoginModal();

    navigate('/');
  };

  const logout = (): void => {
    console.log("Logout function called");
    localStorage.removeItem('token');
    localStorage.removeItem('user'); // Usuwamy użytkownika z localStorage
    setUser(null);

    if (window.location.pathname !== '/') {
      navigate('/');
    }
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

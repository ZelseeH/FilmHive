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
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState<boolean>(false);
  const navigate = useNavigate();

  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;

    const checkAuthStatus = async (): Promise<void> => {
      console.log("Checking auth status...");
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
            setUser(null);
          }
        } else {
          const userData = await response.json();
          setUser(userData);
        }
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          console.error('Error checking authentication status:', error);
        }
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();

    return () => controller.abort();
  }, []);

  const login = (userData: User, token: string): void => {
    console.log("Login function called with:", { userData, tokenExists: !!token });
    localStorage.setItem('token', token);
    setUser(userData);
    closeLoginModal();

    navigate('/');
  };

  const logout = (): void => {
    console.log("Logout function called");
    localStorage.removeItem('token');
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

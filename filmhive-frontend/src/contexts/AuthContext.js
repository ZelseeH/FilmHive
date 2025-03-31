import React, { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const navigate = useNavigate();

  // Sprawdzenie sesji przy ładowaniu strony
  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const checkAuthStatus = async () => {
      console.log("Checking auth status...");
      const token = localStorage.getItem('token');
      console.log("Token from localStorage:", token ? "Token exists" : "No token");
      
      if (token) {
        try {
          console.log("Sending request to /api/user/profile");
          const response = await fetch('http://localhost:5000/api/user/profile', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            signal: controller.signal
          });

          if (!isMounted) return;

          if (response.ok) {
            const userData = await response.json();
            console.log("User data received:", userData);
            setUser(userData);
          } else if (response.status === 401 || response.status === 403) {
            console.error("Token validation failed");
            localStorage.removeItem('token');
          }
        } catch (error) {
          if (error.name !== 'AbortError') {
            console.error('Error checking authentication status:', error);
          }
        }
      }

      if (isMounted) setLoading(false);
    };

    checkAuthStatus();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, []);

  // Funkcja logowania
  const login = (userData, token) => {
    console.log("Login function called with:", { userData, tokenExists: !!token });
    localStorage.setItem('token', token);
    console.log("Token saved to localStorage");
    setUser(userData);
    closeLoginModal();
    
    // Przekierowanie na stronę główną po zalogowaniu
    navigate('/');
  };

  // Funkcja wylogowania
  const logout = () => {
    console.log("Logout function called");
    localStorage.removeItem('token');
    setUser(null);

    // Przekierowanie na stronę główną po wylogowaniu
    navigate('/');
  };

  // Funkcje do zarządzania modalem logowania
  const openLoginModal = () => {
    setIsLoginModalOpen(true);
  };

  const closeLoginModal = () => {
    setIsLoginModalOpen(false);
  };

  // Funkcja do pobierania tokenu (przydatna przy żądaniach API)
  const getToken = () => {
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

export const useAuth = () => useContext(AuthContext);

export default AuthContext;

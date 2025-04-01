import React, { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;

    const checkAuthStatus = async () => {
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
      } catch (error) {
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

  const login = (userData, token) => {
    console.log("Login function called with:", { userData, tokenExists: !!token });
    localStorage.setItem('token', token);
    setUser(userData);
    closeLoginModal();

    navigate('/');
  };

  const logout = () => {
    console.log("Logout function called");
    localStorage.removeItem('token');
    setUser(null);

    if (window.location.pathname !== '/') {
      navigate('/');
    }
  };

  const openLoginModal = () => {
    setIsLoginModalOpen(true);
  };

  const closeLoginModal = () => {
    setIsLoginModalOpen(false);
  };

  const getToken = () => {
    return localStorage.getItem('token') || null;
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

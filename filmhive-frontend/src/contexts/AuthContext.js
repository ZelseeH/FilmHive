// src/contexts/AuthContext.js
import React, { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const navigate = useNavigate(); // Hook do nawigacji

  // Sprawdzenie sesji przy ładowaniu strony
  useEffect(() => {
    const checkAuthStatus = async () => {
      console.log("Checking auth status...");
      const token = localStorage.getItem('token');
      console.log("Token from localStorage:", token ? "Token exists" : "No token");
      
      if (token) {
        try {
          console.log("Token to be sent:", token);
          console.log("Authorization header:", `Bearer ${token}`);
          
          console.log("Sending request to /api/auth/profile");
          const response = await fetch('http://localhost:5000/api/auth/profile', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          console.log("Profile response status:", response.status);
          
          if (response.status === 422 || response.status === 401) {
            const errorData = await response.json();
            console.error("Token validation error:", errorData);
            localStorage.removeItem('token');
          } else if (response.ok) {
            const userData = await response.json();
            console.log("User data received:", userData);
            setUser(userData);
          } else {
            console.log("Invalid token or error response");
            localStorage.removeItem('token');
          }
        } catch (error) {
          console.error('Error checking authentication status:', error);
          localStorage.removeItem('token');
        }
      }
      
      setLoading(false);
    };
    
    checkAuthStatus();
  }, []);

  // Funkcja logowania
  const login = (userData, token) => {
    console.log("Login function called with:", { userData, tokenExists: !!token });
    localStorage.setItem('token', token);
    console.log("Token saved to localStorage");
    setUser(userData);
    closeLoginModal();
    
    // Odświeżenie strony po zalogowaniu
    navigate(0); // Przekazanie 0 do navigate powoduje odświeżenie aktualnej strony
  };

  // Funkcja wylogowania
  const logout = () => {
    console.log("Logout function called");
    localStorage.removeItem('token');
    setUser(null);
    
    // Odświeżenie strony po wylogowaniu
    navigate(0); // Odświeżenie aktualnej strony
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

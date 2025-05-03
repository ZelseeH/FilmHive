import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';

export interface User {
  id: string;
  username: string;
  email: string;
  name?: string;
  bio?: string;
  profile_picture?: string;
  registration_date?: string;
  role: number;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (userData: User, token: string, refreshToken: string) => boolean;
  logout: () => void;
  isLoginModalOpen: boolean;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  getToken: () => string | null;
  refreshAccessToken: () => Promise<string | null>;
  isAdmin: () => boolean;
  isModerator: () => boolean;
  isStaff: () => boolean;
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

  const refreshAccessToken = async (): Promise<string | null> => {
    console.log("🔄 Refreshing access token...");
    const refreshToken = localStorage.getItem('refreshToken');

    if (!refreshToken) {
      console.error("❌ No refresh token available");
      logout();
      return null;
    }

    try {
      const response = await fetch('http://localhost:5000/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refreshToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("❌ Failed to refresh token:", response.status);
        logout();
        return null;
      }

      const data = await response.json();
      localStorage.setItem('accessToken', data.access_token);

      if (data.user) {
        if (!data.user.is_active) {
          console.error("⚠️ Account is suspended");
          logout();
          return null;
        }

        setUser(data.user);
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      return data.access_token;
    } catch (error) {
      console.error("❌ Error refreshing token:", error);
      logout();
      return null;
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;

    const verifyTokenInBackground = async (): Promise<void> => {
      console.log("🔍 Verifying token in background...");
      const token = localStorage.getItem('accessToken');

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch('http://localhost:5000/api/auth/verify-token', {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` },
          signal
        });

        if (!response.ok) {
          if (response.status === 401) {
            console.log("⚠️ Token expired, refreshing...");
            const newToken = await refreshAccessToken();
            if (!newToken) {
              console.error("❌ Failed to refresh token");
            }
          } else if (response.status === 403) {
            console.error("⚠️ Account suspended");
            logout();
          } else {
            console.error("❌ Token validation failed");
            logout();
          }
        } else {
          const userData = await response.json();
          if (userData.user && !userData.user.is_active) {
            console.error("⚠️ Account is suspended");
            logout();
            return;
          }

          setUser(userData.user);
        }
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          console.error('❌ Error verifying token:', error);
        }
      } finally {
        setLoading(false);
      }
    };

    verifyTokenInBackground();

    return () => controller.abort();
  }, []);

  useEffect(() => {
    const originalFetch = window.fetch;

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      try {
        const response = await originalFetch(input, init);

        if (response.status === 401) {
          console.warn("⚠️ Got 401, trying to refresh...");
          const newToken = await refreshAccessToken();

          if (newToken) {
            const newInit = { ...init } as RequestInit;
            if (!newInit.headers) {
              newInit.headers = {};
            }

            if (newInit.headers instanceof Headers) {
              newInit.headers.set('Authorization', `Bearer ${newToken}`);
            } else {
              (newInit.headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`;
            }

            return originalFetch(input, newInit);
          }
        } else if (response.status === 403) {
          try {
            const errorData = await response.clone().json();
            console.log("🚫 Got 403, checking if suspended:", errorData);
            if (errorData.error && errorData.error.includes("zawieszone")) {
              console.error("🚫 Account suspended via 403");
              logout();
            }
          } catch (e) {
            // Ignoruj błędy parsowania JSON
          }
        }

        return response;
      } catch (error) {
        console.error("❌ Fetch error:", error);
        throw error;
      }
    };

    return () => {
      window.fetch = originalFetch;
    };
  }, []);

  const login = (userData: User, token: string, refreshToken: string): boolean => {
    console.log("✅ Login function called with:", { userData, tokenExists: !!token });

    if (!userData.is_active) {
      console.error("❌ Cannot login - account suspended");
      return false;
    }

    localStorage.setItem('accessToken', token);
    localStorage.setItem('refreshToken', refreshToken);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    closeLoginModal();

    return true;
  };

  const logout = (): void => {
    console.log("🚨 Logout triggered!");
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/'); // ⬅️ używamy navigate zamiast reload
  };

  const openLoginModal = (): void => {
    setIsLoginModalOpen(true);
  };

  const closeLoginModal = (): void => {
    setIsLoginModalOpen(false);
  };

  const getToken = (): string | null => {
    return localStorage.getItem('accessToken');
  };

  const isAdmin = (): boolean => user?.role === 1;
  const isModerator = (): boolean => user?.role === 2;
  const isStaff = (): boolean => user?.role === 1 || user?.role === 2;

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
        getToken,
        refreshAccessToken,
        isAdmin,
        isModerator,
        isStaff
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

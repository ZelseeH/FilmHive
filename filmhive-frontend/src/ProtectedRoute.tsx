import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading } = useAuth();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (!loading) {
      // Dodajemy małe opóźnienie, aby upewnić się, że stan autoryzacji jest w pełni zaktualizowany
      const timer = setTimeout(() => {
        setIsReady(true);
      }, 0);

      return () => clearTimeout(timer);
    }
  }, [loading]);

  // Pokazujemy komunikat ładowania dopóki nie jesteśmy gotowi do podjęcia decyzji
  if (loading || !isReady) {
    return <div>Loading...</div>;
  }

  // Przekierowujemy tylko gdy na pewno wiemy, że użytkownik nie jest zalogowany
  if (!user) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};


export default ProtectedRoute;

import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

interface AdminRouteProps {
    children: React.ReactNode;
}

const AdminRoute: React.FC<AdminRouteProps> = ({ children }) => {
    const { user, loading, isAdmin } = useAuth();
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        if (!loading) {
            const timer = setTimeout(() => {
                setIsReady(true);
            }, 0);

            return () => clearTimeout(timer);
        }
    }, [loading]);

    if (loading || !isReady) {
        return <div>Loading...</div>;
    }

    if (!user || !isAdmin()) {
        return <Navigate to="/unauthorized" replace />;
    }

    return <>{children}</>;
};

export default AdminRoute;

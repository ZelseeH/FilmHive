import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

interface StaffRouteProps {
    children: React.ReactNode;
}

const StaffRoute: React.FC<StaffRouteProps> = ({ children }) => {
    const { user, loading, isStaff } = useAuth();
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

    if (!user || !isStaff()) {
        return <Navigate to="/unauthorized" replace />;
    }

    return <>{children}</>;
};

export default StaffRoute;

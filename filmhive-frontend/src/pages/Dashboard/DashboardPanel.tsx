import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar/Sidebar';
import DashboardOverview from './components/DashboardOverview/DashboardOverview';
import { ThemeProvider } from '../../contexts/ThemeContext';
import styles from './DashboardPanel.module.css';
import { useAuth } from '../../contexts/AuthContext';

const DashboardPanelContent: React.FC = () => {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const { isAdmin, isModerator } = useAuth();
    const location = useLocation();

    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth <= 768) {
                setSidebarCollapsed(true);
            }
        };

        window.addEventListener('resize', handleResize);
        handleResize();

        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const toggleSidebar = () => {
        setSidebarCollapsed(!sidebarCollapsed);
    };

    const panelType = isAdmin() ? "Administrator" : isModerator() ? "Moderator" : "Użytkownik";


    const isDashboardHome = location.pathname === '/dashboardpanel' || location.pathname === '/dashboardpanel/';

    return (
        <div className={styles.wrapper}>
            <Sidebar collapsed={sidebarCollapsed} toggleSidebar={toggleSidebar} />

            <div className={`${styles.mainContent} ${sidebarCollapsed ? styles.expanded : ''}`}>
                <main className={styles.content}>
                    {isDashboardHome ? <DashboardOverview /> : <Outlet />}
                </main>

                <footer className={styles.footer}>
                    <div>
                        &copy; {new Date().getFullYear()} FilmHive {panelType} Panel Wersja 1.0
                    </div>
                </footer>
            </div>
        </div>
    );
};


const DashboardPanel: React.FC<React.PropsWithChildren<{}>> = () => {
    return (
        <ThemeProvider>
            <DashboardPanelContent />
        </ThemeProvider>
    );
};

export default DashboardPanel;

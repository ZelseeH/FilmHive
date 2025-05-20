import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar/Sidebar';
import styles from './DashboardPanel.module.css';
import { useAuth } from '../../contexts/AuthContext';

const DashboardPanel: React.FC<React.PropsWithChildren<{}>> = () => {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const { isAdmin, isModerator } = useAuth();

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

    return (
        <div className={styles.wrapper}>
            <Sidebar collapsed={sidebarCollapsed} toggleSidebar={toggleSidebar} />

            <div className={`${styles.mainContent} ${sidebarCollapsed ? styles.expanded : ''}`}>
                <main className={styles.content}>
                    <Outlet />
                </main>

                <footer className={styles.footer}>
                    <div>
                        &copy; {new Date().getFullYear()} FilmHive {panelType} Panel Wersja 1.0
                    </div>
                </footer>
            </div>
        </div >
    );
};

export default DashboardPanel;

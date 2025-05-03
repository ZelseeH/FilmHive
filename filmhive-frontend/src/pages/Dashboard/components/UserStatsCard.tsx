// src/pages/Dashboard/components/UserStatsCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import styles from '../Dashboard.module.css';

interface UserStatsProps {
    userStats: {
        total: number;
        active: number;
        admins: number;
        moderators: number;
    };
}

const UserStatsCard: React.FC<UserStatsProps> = ({ userStats }) => {
    return (
        <div className={styles.widgetCard}>
            <div className={styles.widgetHeader}>
                <h2 className={styles.widgetTitle}>Użytkownicy</h2>
            </div>
            <div className={styles.widgetContent}>
                <div className={styles.widgetStat}>
                    <span className={`${styles.statLabel} ${styles.totalLabel}`}>Łącznie:</span>
                    <span className={styles.statValue}>{userStats.total}</span>
                </div>
                <div className={styles.widgetStat}>
                    <span className={`${styles.statLabel} ${styles.activeLabel}`}>Aktywni:</span>
                    <span className={styles.statValue}>{userStats.active}</span>
                </div>
                <div className={styles.widgetStat}>
                    <span className={`${styles.statLabel} ${styles.adminLabel}`}>Administratorzy:</span>
                    <span className={styles.statValue}>{userStats.admins}</span>
                </div>
                <div className={styles.widgetStat}>
                    <span className={`${styles.statLabel} ${styles.moderatorLabel}`}>Moderatorzy:</span>
                    <span className={styles.statValue}>{userStats.moderators}</span>
                </div>
                <div className={styles.widgetStat}>
                    <span className={`${styles.statLabel} ${styles.userLabel}`}>Zwykli:</span>
                    <span className={styles.statValue}>
                        {userStats.total - userStats.admins - userStats.moderators}
                    </span>
                </div>
            </div>
            <Link to="/dashboard/users" className={styles.widgetLink}>
                Zarządzaj
            </Link>
        </div>
    );
};

export default UserStatsCard;

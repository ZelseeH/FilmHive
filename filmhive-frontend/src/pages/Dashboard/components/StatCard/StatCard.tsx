import React from 'react';
import styles from './StatCard.module.css';

interface StatCardProps {
    title: string;
    value: number | string;
    icon: string;
    color: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'orange';
    subtitle?: string;
    suffix?: string;
}

const StatCard: React.FC<StatCardProps> = ({
    title,
    value,
    icon,
    color,
    subtitle,
    suffix = ''
}) => {
    return (
        <div className={`${styles.card} ${styles[color]}`}>
            <div className={styles.header}>
                <div className={styles.icon}>{icon}</div>
                <h3 className={styles.title}>{title}</h3>
            </div>
            <div className={styles.content}>
                <div className={styles.value}>
                    {typeof value === 'number' ? value.toLocaleString() : value}
                    {suffix}
                </div>
                {subtitle && <div className={styles.subtitle}>{subtitle}</div>}
            </div>
        </div>
    );
};

export default StatCard;

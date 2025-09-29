import React from 'react';
import styles from './NotificationBadge.module.css';

interface NotificationBadgeProps {
    count: number;
    onClick: () => void;
}

const NotificationBadge: React.FC<NotificationBadgeProps> = ({ count, onClick }) => {
    const displayCount = count > 9 ? '9+' : count.toString();

    return (
        <div className={styles.badgeContainer} onClick={onClick}>
            <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="currentColor"
                className={styles.bellIcon}
            >
                <path d="M10 2C8.14 2 6.59 3.28 6.14 5.01L6 5.5V10L4.5 12H15.5L14 10V5.5C14 3.57 12.43 2 10.5 2H10Z" />
                <path d="M8 16C8 17.1 8.9 18 10 18C11.1 18 12 17.1 12 16" />
            </svg>
            {/* Badge tylko gdy count > 0 */}
            {count > 0 && (
                <span className={styles.badge}>
                    {displayCount}
                </span>
            )}
        </div>
    );
};

export default NotificationBadge;

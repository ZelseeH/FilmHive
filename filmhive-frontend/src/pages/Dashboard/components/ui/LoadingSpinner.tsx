import React from 'react';
import styles from './LoadingSpinner.module.css';

const LoadingSpinner: React.FC = () => {
    return (
        <div className={styles.loadingSpinner}>
            <div className={styles.spinner} />
        </div>
    );
};

export default LoadingSpinner;

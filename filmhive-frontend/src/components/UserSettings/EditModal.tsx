import React, { ReactNode } from 'react';
import styles from './UserSettings.module.css';

interface EditModalProps {
    title: string;
    error: string;
    loading: boolean;
    onCancel: () => void;
    onSave: () => void;
    children: ReactNode;
}

const EditModal: React.FC<EditModalProps> = ({
    title,
    error,
    loading,
    onCancel,
    onSave,
    children
}) => {
    return (
        <div className={styles['modal-overlay']}>
            <div className={styles['edit-modal']}>
                <h2>{title}</h2>

                {error && (
                    <div className={styles['modal-error']}>
                        {error}
                    </div>
                )}

                {children}

                <div className={styles['modal-actions']}>
                    <button onClick={onCancel}>Anuluj</button>
                    <button onClick={onSave} disabled={loading}>
                        {loading ? 'Zapisywanie...' : 'Zapisz'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EditModal;

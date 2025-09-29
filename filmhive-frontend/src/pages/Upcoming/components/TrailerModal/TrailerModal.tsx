import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import styles from './TrailerModal.module.css';

interface TrailerModalProps {
    isOpen: boolean;
    onClose: () => void;
    trailerUrl: string;
    movieTitle: string;
}

const TrailerModal: React.FC<TrailerModalProps> = ({
    isOpen,
    onClose,
    trailerUrl,
    movieTitle
}) => {
    const getYouTubeVideoId = (url: string): string | null => {
        const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
        return match ? match[1] : null;
    };

    // Blokowanie scrollowania
    useEffect(() => {
        if (isOpen) {
            const scrollY = window.scrollY;
            document.body.style.position = 'fixed';
            document.body.style.top = `-${scrollY}px`;
            document.body.style.width = '100%';
            document.body.style.overflow = 'hidden';
            document.documentElement.style.overflow = 'hidden';
        } else {
            const scrollY = document.body.style.top;
            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.width = '';
            document.body.style.overflow = '';
            document.documentElement.style.overflow = '';

            if (scrollY) {
                window.scrollTo(0, parseInt(scrollY || '0') * -1);
            }
        }

        return () => {
            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.width = '';
            document.body.style.overflow = '';
            document.documentElement.style.overflow = '';
        };
    }, [isOpen]);

    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                onClose();
            }
        };

        const handleClickAnywhere = (e: MouseEvent) => {
            const modal = document.querySelector(`.${styles.modal}`);
            if (modal && !modal.contains(e.target as Node)) {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.addEventListener('click', handleClickAnywhere, true);
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.removeEventListener('click', handleClickAnywhere, true);
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const videoId = getYouTubeVideoId(trailerUrl);

    if (!videoId) return null;

    const modalContent = (
        <div className={styles.overlay}>
            <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
                <button className={styles.closeButton} onClick={onClose}>
                    ×
                </button>
                <h3 className={styles.title}>{movieTitle} - Zwiastun</h3>
                <div className={styles.videoContainer}>
                    <iframe
                        src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`}
                        title={`${movieTitle} - Zwiastun`}
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                    />
                </div>
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
};

export default TrailerModal;

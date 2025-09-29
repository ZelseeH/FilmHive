import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { NotificationItem } from '../../services/notificationService';
import { createSlug } from '../../../../utils/formatters';
import styles from './NotificationsPopup.module.css';

interface NotificationsPopupProps {
    notifications: NotificationItem[];
    isOpen: boolean;
    onClose: () => void;
    onMarkAsRead: (id: number) => void;
    onMarkAllAsRead: () => void;
    onNotificationClick?: (notificationId: number) => Promise<string | null>;
    isLoading?: boolean;
}

const NotificationsPopup: React.FC<NotificationsPopupProps> = ({
    notifications,
    isOpen,
    onClose,
    onMarkAsRead,
    onMarkAllAsRead,
    onNotificationClick,
    isLoading = false
}) => {
    const navigate = useNavigate();
    const popupRef = useRef<HTMLDivElement>(null);
    const [showUnreadOnly, setShowUnreadOnly] = useState(true);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (popupRef.current && !popupRef.current.contains(event.target as Node)) {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen, onClose]);

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Teraz';
        if (minutes < 60) return `${minutes} min temu`;
        if (hours < 24) return `${hours} godz temu`;
        if (days < 7) return `${days} dni temu`;
        return date.toLocaleDateString('pl-PL');
    };

    const handleNotificationClick = async (notification: NotificationItem) => {
        try {
            // Oznacz jako przeczytane jeśli nie było
            if (!notification.is_read) {
                onMarkAsRead(notification.id);
            }

            // Przejdź do filmu z kotwicą do komentarza/odpowiedzi
            if (notification.movie) {
                const movieSlug = createSlug(notification.movie.title);
                let url = `/movie/details/${movieSlug}`;

                // Dodaj hash do konkretnego komentarza/odpowiedzi
                if (notification.reply_id) {
                    url += `#reply-${notification.reply_id}`;
                } else if (notification.comment_id) {
                    url += `#comment-${notification.comment_id}`;
                }

                navigate(url);
                onClose();
                return;
            }

            // Fallback - użyj originalnej logiki
            if (onNotificationClick) {
                const redirectUrl = await onNotificationClick(notification.id);
                if (redirectUrl) {
                    navigate(redirectUrl);
                    onClose();
                    return;
                }
            }

            if (notification.movie_url) {
                navigate(notification.movie_url);
                onClose();
            } else if (notification.comment_id) {
                navigate(`/movie/comment/${notification.comment_id}`);
                onClose();
            }
        } catch (error) {
            console.error('Error handling notification click:', error);
            if (!notification.is_read) {
                onMarkAsRead(notification.id);
            }
        }
    };

    // Filtrowanie powiadomień
    const filteredNotifications = showUnreadOnly
        ? notifications.filter(n => !n.is_read)
        : notifications;

    const unreadCount = notifications.filter(n => !n.is_read).length;

    if (!isOpen) return null;

    return (
        <div className={styles.overlay}>
            <div className={styles.popup} ref={popupRef}>
                <div className={styles.header}>
                    <h3>
                        Powiadomienia
                        {unreadCount > 0 && (
                            <span className={styles.unreadBadge}>
                                {unreadCount}
                            </span>
                        )}
                    </h3>
                    <div className={styles.headerActions}>
                        <button
                            onClick={() => setShowUnreadOnly(!showUnreadOnly)}
                            className={`${styles.toggleButton} ${showUnreadOnly ? styles.active : ''}`}
                            title={showUnreadOnly ? "Pokaż wszystkie" : "Pokaż tylko nieprzeczytane"}
                        >
                            {showUnreadOnly ? "Wszystkie" : "Nieprzeczytane"}
                        </button>

                        {unreadCount > 0 && (
                            <button
                                onClick={onMarkAllAsRead}
                                className={styles.markAllButton}
                                disabled={isLoading}
                                title="Oznacz wszystkie jako przeczytane"
                            >
                                ✓ Wszystkie
                            </button>
                        )}

                        <button
                            onClick={onClose}
                            className={styles.closeButton}
                            title="Zamknij"
                        >
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                                <path
                                    d="M15 5L5 15M5 5L15 15"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                />
                            </svg>
                        </button>
                    </div>
                </div>

                <div className={styles.content}>
                    {isLoading ? (
                        <div className={styles.loading}>
                            <div className={styles.spinner}></div>
                            <span>Ładowanie powiadomień...</span>
                        </div>
                    ) : filteredNotifications.length === 0 ? (
                        <div className={styles.empty}>
                            <div className={styles.emptyIcon}>🔔</div>
                            <p>
                                {showUnreadOnly
                                    ? "Brak nieprzeczytanych powiadomień"
                                    : "Brak powiadomień"
                                }
                            </p>
                            <small>
                                {showUnreadOnly
                                    ? "Wszystkie powiadomienia zostały przeczytane"
                                    : "Gdy ktoś skomentuje Twój film, zobaczysz to tutaj"
                                }
                            </small>
                        </div>
                    ) : (
                        <div className={styles.notificationsList}>
                            {filteredNotifications.map((notification) => (
                                <div
                                    key={notification.id}
                                    className={`${styles.notificationItem} ${!notification.is_read ? styles.unread : ''}`}
                                    onClick={() => handleNotificationClick(notification)}
                                    role="button"
                                    tabIndex={0}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' || e.key === ' ') {
                                            handleNotificationClick(notification);
                                        }
                                    }}
                                >
                                    <div className={styles.notificationAvatar}>
                                        {notification.from_user?.profile_picture ? (
                                            <img
                                                src={notification.from_user.profile_picture}
                                                alt={notification.from_user.username}
                                                loading="lazy"
                                            />
                                        ) : (
                                            <div className={styles.defaultAvatar}>
                                                {notification.from_user?.username.charAt(0).toUpperCase() || '?'}
                                            </div>
                                        )}
                                    </div>

                                    <div className={styles.notificationContent}>
                                        {notification.movie && (
                                            <div className={styles.movieInfo}>
                                                <span className={styles.movieTitle}>
                                                    📽️ {notification.movie.title}
                                                </span>
                                            </div>
                                        )}

                                        <p className={styles.message}>
                                            {notification.message}
                                        </p>

                                        <span className={styles.time}>
                                            {formatDate(notification.created_at)}
                                        </span>
                                    </div>

                                    {!notification.is_read && (
                                        <div
                                            className={styles.unreadDot}
                                            aria-label="Nieprzeczytane"
                                        ></div>
                                    )}

                                    {!notification.is_read && (
                                        <button
                                            className={styles.markReadButton}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onMarkAsRead(notification.id);
                                            }}
                                            title="Oznacz jako przeczytane"
                                            aria-label="Oznacz jako przeczytane"
                                        >
                                            ✓
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {notifications.length > 0 && (
                    <div className={styles.footer}>
                        <div className={styles.footerInfo}>
                            <small>
                                Wyświetlone: {filteredNotifications.length} z {notifications.length} powiadomień
                                {unreadCount > 0 && ` • ${unreadCount} nieprzeczytanych`}
                            </small>
                        </div>
                        <button
                            onClick={() => {
                                navigate('/notifications');
                                onClose();
                            }}
                            className={styles.viewAllButton}
                        >
                            Zobacz wszystkie powiadomienia
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default NotificationsPopup;

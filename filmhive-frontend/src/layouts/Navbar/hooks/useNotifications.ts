// src/hooks/useNotifications.ts
import { useState, useEffect, useCallback } from 'react';
import {
    getNotifications,
    getUnreadCount,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    clickNotification,
    NotificationItem
} from '../services/notificationService';

const POLLING_INTERVAL = 10000; // 10 sekund

export const useNotifications = () => {
    const [notifications, setNotifications] = useState<NotificationItem[]>([]);
    const [unreadCount, setUnreadCount] = useState<number>(0);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    // Pobiera powiadomienia (CIĘŻKA operacja - cała lista)
    const fetchNotifications = useCallback(async (limit: number = 50) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await getNotifications(limit, true);
            if (response.success) {
                setNotifications(response.data.notifications);
                setUnreadCount(response.data.unread_count);
            } else {
                setError(response.error || 'Błąd podczas pobierania powiadomień');
            }
        } catch (err: any) {
            setError(err.message || 'Nieoczekiwany błąd');
            console.error('Error fetching notifications:', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Pobiera licznik nieprzeczytanych (LEKKA operacja - tylko liczba)
    const fetchUnreadCount = useCallback(async () => {
        try {
            const response = await getUnreadCount();
            setUnreadCount(response.unread_count);
        } catch (err: any) {
            console.error('Error fetching unread count:', err);
        }
    }, []);

    // Oznacza powiadomienie jako przeczytane
    const handleMarkAsRead = useCallback(async (notificationId: number) => {
        try {
            // Optymistycznie aktualizuj UI
            setNotifications(prev =>
                prev.map(n =>
                    n.id === notificationId
                        ? { ...n, is_read: true }
                        : n
                )
            );
            setUnreadCount(prev => Math.max(0, prev - 1));

            const response = await markNotificationAsRead(notificationId);
            if (!response.success) {
                // Przywróć stan w razie błędu
                fetchNotifications();
            }
        } catch (err: any) {
            console.error('Error marking notification as read:', err);
            setError(err.message || 'Błąd podczas oznaczania powiadomienia');
            fetchNotifications(); // Przywróć stan
        }
    }, [fetchNotifications]);

    // Oznacza wszystkie jako przeczytane
    const handleMarkAllAsRead = useCallback(async () => {
        try {
            // Optymistycznie aktualizuj UI
            setNotifications(prev =>
                prev.map(n => ({ ...n, is_read: true }))
            );
            setUnreadCount(0);

            const response = await markAllNotificationsAsRead();
            if (!response.success) {
                fetchNotifications();
            }
        } catch (err: any) {
            console.error('Error marking all notifications as read:', err);
            setError(err.message || 'Błąd podczas oznaczania powiadomień');
            fetchNotifications();
        }
    }, [fetchNotifications]);

    // Obsługuje kliknięcie w powiadomienie
    const handleNotificationClick = useCallback(async (notificationId: number) => {
        try {
            const notification = notifications.find(n => n.id === notificationId);

            // Optymistycznie oznacz jako przeczytane
            if (notification && !notification.is_read) {
                setNotifications(prev =>
                    prev.map(n =>
                        n.id === notificationId
                            ? { ...n, is_read: true }
                            : n
                    )
                );
                setUnreadCount(prev => Math.max(0, prev - 1));
            }

            const response = await clickNotification(notificationId);
            if (response.success) {
                return response.redirect_url;
            }
        } catch (err: any) {
            console.error('Error handling notification click:', err);
            setError(err.message || 'Błąd podczas przetwarzania powiadomienia');
        }
        return null;
    }, [notifications]);

    // ✅ POLLING - Automatyczne odświeżanie licznika co 10 sekund
    useEffect(() => {
        // Pierwsze pobranie przy montowaniu
        fetchUnreadCount();

        // Ustaw interwał pollingu
        const intervalId = setInterval(() => {
            fetchUnreadCount();
        }, POLLING_INTERVAL);

        // Cleanup przy unmount
        return () => {
            clearInterval(intervalId);
        };
    }, [fetchUnreadCount]);

    // ✅ Inicjalne pobieranie pełnej listy powiadomień
    useEffect(() => {
        fetchNotifications();
    }, [fetchNotifications]);

    return {
        notifications,
        unreadCount,
        isLoading,
        error,
        fetchNotifications,
        markAsRead: handleMarkAsRead,
        markAllAsRead: handleMarkAllAsRead,
        notificationClick: handleNotificationClick,
        refreshNotifications: fetchNotifications,
        refreshUnreadCount: fetchUnreadCount
    };
};

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

export const useNotifications = () => {
    const [notifications, setNotifications] = useState<NotificationItem[]>([]);
    const [unreadCount, setUnreadCount] = useState<number>(0);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    // Pobiera powiadomienia
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

    // Pobiera licznik nieprzeczytanych
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
            const response = await markNotificationAsRead(notificationId);
            if (response.success) {
                // Aktualizuj lokalne powiadomienia
                setNotifications(prev =>
                    prev.map(n =>
                        n.id === notificationId
                            ? { ...n, is_read: true }
                            : n
                    )
                );
                // Aktualizuj licznik
                setUnreadCount(prev => Math.max(0, prev - 1));
            }
        } catch (err: any) {
            console.error('Error marking notification as read:', err);
            setError(err.message || 'Błąd podczas oznaczania powiadomienia');
        }
    }, []);

    // Oznacza wszystkie jako przeczytane
    const handleMarkAllAsRead = useCallback(async () => {
        try {
            const response = await markAllNotificationsAsRead();
            if (response.success) {
                // Aktualizuj wszystkie powiadomienia na przeczytane
                setNotifications(prev =>
                    prev.map(n => ({ ...n, is_read: true }))
                );
                setUnreadCount(0);
            }
        } catch (err: any) {
            console.error('Error marking all notifications as read:', err);
            setError(err.message || 'Błąd podczas oznaczania powiadomień');
        }
    }, []);

    // Obsługuje kliknięcie w powiadomienie
    const handleNotificationClick = useCallback(async (notificationId: number) => {
        try {
            const response = await clickNotification(notificationId);
            if (response.success) {
                // Oznacz jako przeczytane lokalnie
                setNotifications(prev =>
                    prev.map(n =>
                        n.id === notificationId
                            ? { ...n, is_read: true }
                            : n
                    )
                );
                // Zmniejsz licznik jeśli było nieprzeczytane
                const notification = notifications.find(n => n.id === notificationId);
                if (notification && !notification.is_read) {
                    setUnreadCount(prev => Math.max(0, prev - 1));
                }

                return response.redirect_url;
            }
        } catch (err: any) {
            console.error('Error handling notification click:', err);
            setError(err.message || 'Błąd podczas przetwarzania powiadomienia');
        }
        return null;
    }, [notifications]);

    // Inicjalne pobieranie przy montowaniu
    useEffect(() => {
        fetchNotifications();
        fetchUnreadCount();
    }, [fetchNotifications, fetchUnreadCount]);

    // Auto-refresh co 30 sekund (opcjonalne)
    useEffect(() => {
        const interval = setInterval(() => {
            fetchUnreadCount();
        }, 30000);

        return () => clearInterval(interval);
    }, [fetchUnreadCount]);

    return {
        notifications,
        unreadCount,
        isLoading,
        error,
        fetchNotifications,
        markAsRead: handleMarkAsRead,           // ← zmiana nazwy
        markAllAsRead: handleMarkAllAsRead,     // ← zmiana nazwy  
        notificationClick: handleNotificationClick, // ← zmiana nazwy
        refreshNotifications: fetchNotifications,
        refreshUnreadCount: fetchUnreadCount
    };
};

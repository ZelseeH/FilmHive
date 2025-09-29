// src/services/notificationService.ts
import { fetchWithAuth } from '../../../services/api';

export interface NotificationItem {
    id: number;
    user_id: number;
    from_user_id: number;
    comment_id?: number;
    reply_id?: number;
    message: string;
    is_read: boolean;
    created_at: string;
    from_user?: {
        id: number;
        username: string;
        profile_picture?: string;
    };
    movie?: {
        id: number;
        title: string;
        poster_url?: string;
    };
    movie_url?: string;
}

export interface NotificationsResponse {
    success: boolean;
    data: {
        notifications: NotificationItem[];
        total_count: number;
        unread_count: number;
    };
    error?: string;
}

export interface NotificationStats {
    success: boolean;
    data: {
        total_count: number;
        unread_count: number;
        read_count: number;
    };
}

export interface CreateNotificationData {
    user_id: number;
    message: string;
    comment_id?: number;
    reply_id?: number;
}

export interface NotificationClickResponse {
    success: boolean;
    message: string;
    redirect_url?: string;
    movie_id?: number;
    comment_id?: number;
    reply_id?: number;
}

// Pobiera wszystkie powiadomienia użytkownika
export const getNotifications = async (
    limit: number = 50,
    includeMovie: boolean = true
): Promise<NotificationsResponse> => {
    try {
        const queryParams = new URLSearchParams({
            limit: limit.toString(),
            include_movie: includeMovie.toString()
        });

        return await fetchWithAuth(`notifications?${queryParams.toString()}`);
    } catch (error) {
        console.error('Error fetching notifications:', error);
        throw error;
    }
};

// Pobiera nieprzeczytane powiadomienia
export const getUnreadNotifications = async (): Promise<NotificationsResponse> => {
    try {
        return await fetchWithAuth('notifications/unread');
    } catch (error) {
        console.error('Error fetching unread notifications:', error);
        throw error;
    }
};

// Pobiera liczbę nieprzeczytanych powiadomień
export const getUnreadCount = async (): Promise<{ unread_count: number }> => {
    try {
        return await fetchWithAuth('notifications/unread-count');
    } catch (error) {
        console.error('Error fetching unread count:', error);
        throw error;
    }
};

// Oznacza powiadomienie jako przeczytane
export const markNotificationAsRead = async (notificationId: number): Promise<{ success: boolean; message: string }> => {
    try {
        return await fetchWithAuth(`notifications/${notificationId}/read`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Error marking notification as read:', error);
        throw error;
    }
};

// Obsługuje kliknięcie w powiadomienie (oznacza jako przeczytane + zwraca URL)
export const clickNotification = async (notificationId: number): Promise<NotificationClickResponse> => {
    try {
        return await fetchWithAuth(`notifications/${notificationId}/click`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Error handling notification click:', error);
        throw error;
    }
};

// Oznacza wszystkie powiadomienia jako przeczytane
export const markAllNotificationsAsRead = async (): Promise<{ success: boolean; message: string; marked_count: number }> => {
    try {
        return await fetchWithAuth('notifications/read-all', {
            method: 'POST'
        });
    } catch (error) {
        console.error('Error marking all notifications as read:', error);
        throw error;
    }
};

// Pobiera statystyki powiadomień
export const getNotificationStats = async (): Promise<NotificationStats> => {
    try {
        return await fetchWithAuth('notifications/stats');
    } catch (error) {
        console.error('Error fetching notification stats:', error);
        throw error;
    }
};

// Pobiera powiadomienia dla konkretnego komentarza
export const getNotificationsByComment = async (commentId: number): Promise<{
    success: boolean;
    data: {
        notifications: NotificationItem[];
        count: number;
    };
}> => {
    try {
        return await fetchWithAuth(`notifications/comment/${commentId}`);
    } catch (error) {
        console.error('Error fetching notifications by comment:', error);
        throw error;
    }
};

// Tworzy nowe powiadomienie
export const createNotification = async (data: CreateNotificationData): Promise<{
    success: boolean;
    notification?: NotificationItem;
    message: string;
}> => {
    try {
        return await fetchWithAuth('notifications/create', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    } catch (error) {
        console.error('Error creating notification:', error);
        throw error;
    }
};

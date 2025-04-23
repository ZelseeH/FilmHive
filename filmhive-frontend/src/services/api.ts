const API_URL = 'http://localhost:5000/api';

export const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('token');

    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        ...options.headers
    };

    const response = await fetch(`${API_URL}/${endpoint}`, {
        ...options,
        headers,
        cache: 'no-store'
    } as RequestInit);

    if (!response.ok) {
        try {
            const error = await response.json();
            throw new Error(error.error || 'Wystąpił błąd');
        } catch (e) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
    }

    return response.json();
};

export const clearAuthAndCache = () => {
    localStorage.removeItem('token');

    if ('caches' in window) {
        try {
            caches.keys().then(cacheNames => {
                cacheNames.forEach(cacheName => {
                    caches.delete(cacheName);
                });
            });
        } catch (e) {
            console.error('Error clearing cache:', e);
        }
    }

    if (navigator.serviceWorker) {
        navigator.serviceWorker.getRegistrations().then(registrations => {
            registrations.forEach(registration => {
                registration.unregister();
            });
        });
    }
};

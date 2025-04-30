const API_URL = 'http://localhost:5000/api';

export const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('token');

    // Ustaw nagłówki, zachowując możliwość nadpisania przez options.headers
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
<<<<<<< Updated upstream
        ...options.headers
=======
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        ...(options.headers || {})
>>>>>>> Stashed changes
    };

    const response = await fetch(`${API_URL}/${endpoint}`, {
        ...options,
<<<<<<< Updated upstream
        headers
=======
        headers,
        cache: 'no-store'
>>>>>>> Stashed changes
    });

    // Obsługa błędów z backendu (Marshmallow zawsze zwraca { error: ... } w przypadku błędu)
    if (!response.ok) {
<<<<<<< Updated upstream
        const error = await response.json();
        throw new Error(error.error || 'Wystąpił błąd');
=======
        let errorMessage = `HTTP error! Status: ${response.status}`;
        try {
            const error = await response.json();
            errorMessage = error?.error || errorMessage;
        } catch (e) {
            // Jeśli odpowiedź nie jest JSON-em, zostaw domyślny komunikat
        }
        throw new Error(errorMessage);
>>>>>>> Stashed changes
    }

    // Zwróć sparsowaną odpowiedź JSON
    return response.json();
};
<<<<<<< Updated upstream
=======

export const clearAuthAndCache = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');

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
>>>>>>> Stashed changes

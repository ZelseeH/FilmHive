const API_URL = 'http://localhost:5000/api';

export const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('accessToken'); 

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
            const errorData = await response.json();
            const error: any = new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            error.response = response; // Dodajemy obiekt response do błędu
            throw error;
        } catch (e) {
            // Jeśli nie możemy sparsować JSON, tworzymy błąd z informacją o statusie
            const error: any = new Error(`HTTP error! Status: ${response.status}`);
            error.response = response;
            throw error;
        }
    }

    return response.json();
};

export const clearAuthAndCache = () => {
    localStorage.removeItem('accessToken'); // Zmieniono z 'token' na 'accessToken'
    localStorage.removeItem('refreshToken'); // Dodano usuwanie refresh tokenu
    localStorage.removeItem('user'); // Dodano usuwanie danych użytkownika

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

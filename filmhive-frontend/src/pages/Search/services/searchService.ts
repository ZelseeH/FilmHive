// src/services/searchService.ts

const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
};

export const searchMovies = async (query: string, page = 1, perPage = 10) => {
    const headers = getAuthHeaders();
    const res = await fetch(
        `/api/movies/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`,
        { headers }
    );
    return res.json();
};

export const searchPeople = async (query: string, page = 1, perPage = 10, type?: 'actor' | 'director') => {
    const headers = getAuthHeaders();
    let url = `/api/people/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`;

    if (type) {
        url += `&type=${type}`;
    }

    const res = await fetch(url, { headers });
    return res.json();
};

// Zachowujemy dla kompatybilności wstecznej
export const searchActors = async (query: string, page = 1, perPage = 10) => {
    return searchPeople(query, page, perPage, 'actor');
};

export const searchUsers = async (query: string, page = 1, perPage = 10) => {
    const headers = getAuthHeaders();
    const res = await fetch(
        `/api/user/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`,
        { headers }
    );
    return res.json();
};

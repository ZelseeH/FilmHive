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

export const searchActors = async (query: string, page = 1, perPage = 10) => {
    const headers = getAuthHeaders();
    const res = await fetch(
        `/api/actors/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`,
        { headers }
    );
    return res.json();
};

export const searchUsers = async (query: string, page = 1, perPage = 10) => {
    const headers = getAuthHeaders();
    const res = await fetch(
        `/api/user/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`,
        { headers }
    );
    return res.json();
};

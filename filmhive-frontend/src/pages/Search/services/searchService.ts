export const searchMovies = async (query: string, page = 1, perPage = 10) => {
    const res = await fetch(`/api/movies/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`);
    return res.json();
};

export const searchActors = async (query: string, page = 1, perPage = 10) => {
    const res = await fetch(`/api/actors/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`);
    return res.json();
};

export const searchUsers = async (query: string, page = 1, perPage = 10) => {
    const res = await fetch(`/api/user/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`);
    return res.json();
};

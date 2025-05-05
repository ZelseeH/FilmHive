export interface Genre {
    id: number;
    name: string;
}

const API_URL = 'http://localhost:5000/api/genres';

export const fetchGenres = async (token: string): Promise<Genre[]> => {
    const res = await fetch(API_URL, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Nie udało się pobrać gatunków');
    return await res.json();
};

export const addGenre = async (token: string, name: string): Promise<Genre> => {
    const res = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name })
    });
    if (!res.ok) throw new Error('Nie udało się dodać gatunku');
    return await res.json();
};

export const updateGenre = async (token: string, id: number, name: string): Promise<Genre> => {
    const res = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name })
    });
    if (!res.ok) throw new Error('Nie udało się edytować gatunku');
    return await res.json();
};

export const deleteGenre = async (token: string, id: number): Promise<void> => {
    const res = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Nie udało się usunąć gatunku');
};

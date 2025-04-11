export class watchlistService {
    static async addToWatchlist(movieId: number, token: string): Promise<void> {
        const response = await fetch(`http://localhost:5000/api/watchlist/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ movie_id: movieId })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się dodać do listy do obejrzenia: ${response.status}`);
        }
    }

    static async removeFromWatchlist(movieId: number, token: string): Promise<void> {
        const response = await fetch(`http://localhost:5000/api/watchlist/remove?movie_id=${movieId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się usunąć z listy do obejrzenia: ${response.status}`);
        }
    }

    static async checkIfInWatchlist(movieId: number, token: string): Promise<boolean> {
        const response = await fetch(`http://localhost:5000/api/watchlist/check/${movieId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się sprawdzić statusu: ${response.status}`);
        }

        const data = await response.json();
        return data.is_in_watchlist ?? false;
    }

    static async getUserWatchlist(token: string, page: number = 1, perPage: number = 10): Promise<any> {
        const response = await fetch(`http://localhost:5000/api/watchlist/user?page=${page}&per_page=${perPage}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się pobrać listy do obejrzenia: ${response.status}`);
        }

        return await response.json();
    }

    static async getMovieWatchlistCount(movieId: number): Promise<number> {
        const response = await fetch(`http://localhost:5000/api/watchlist/count/${movieId}`);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się pobrać liczby osób chcących obejrzeć: ${response.status}`);
        }

        const data = await response.json();
        return data.count ?? 0;
    }
}

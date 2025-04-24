export class watchlistService {
    static async addToWatchlist(movieId: number, token: string): Promise<void> {
        try {
            const response = await fetch(`http://localhost:5000/api/watchlist/add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache, no-store, must-revalidate'
                },
                body: JSON.stringify({ movie_id: movieId })
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Error adding to watchlist:', errorData);
                throw new Error(`Nie udało się dodać do listy do obejrzenia: ${response.status}`);
            }
        } catch (error) {
            console.error('Network error adding to watchlist:', error);
            throw error;
        }
    }

    static async removeFromWatchlist(movieId: number, token: string): Promise<void> {
        try {
            const response = await fetch(`http://localhost:5000/api/watchlist/remove?movie_id=${movieId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache, no-store, must-revalidate'
                }
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Error removing from watchlist:', errorData);
                throw new Error(`Nie udało się usunąć z listy do obejrzenia: ${response.status}`);
            }
        } catch (error) {
            console.error('Network error removing from watchlist:', error);
            throw error;
        }
    }

    static async checkIfInWatchlist(movieId: number, token: string): Promise<boolean> {
        try {
            // Dodajemy timestamp, aby uniknąć cachowania
            const timestamp = new Date().getTime();
            const response = await fetch(`http://localhost:5000/api/watchlist/check/${movieId}?_=${timestamp}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache, no-store, must-revalidate'
                }
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Error checking watchlist status:', errorData);
                throw new Error(`Nie udało się sprawdzić statusu: ${response.status}`);
            }

            const data = await response.json();
            return data.is_in_watchlist ?? false;
        } catch (error) {
            console.error('Network error checking watchlist status:', error);
            throw error;
        }
    }

    static async getUserWatchlist(token: string, page: number = 1, perPage: number = 10): Promise<any> {
        try {
            const response = await fetch(`http://localhost:5000/api/watchlist/user?page=${page}&per_page=${perPage}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache, no-store, must-revalidate'
                }
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Error getting user watchlist:', errorData);
                throw new Error(`Nie udało się pobrać listy do obejrzenia: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Network error getting user watchlist:', error);
            throw error;
        }
    }

    static async getMovieWatchlistCount(movieId: number): Promise<number> {
        try {
            const response = await fetch(`http://localhost:5000/api/watchlist/count/${movieId}`);

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Error getting watchlist count:', errorData);
                throw new Error(`Nie udało się pobrać liczby osób chcących obejrzeć: ${response.status}`);
            }

            const data = await response.json();
            return data.count ?? 0;
        } catch (error) {
            console.error('Network error getting watchlist count:', error);
            throw error;
        }
    }

    static async getUserRecentWatchlist(token: string, limit: number = 6): Promise<any> {
        try {
            const response = await fetch(`http://localhost:5000/api/watchlist/user/recent?limit=${limit}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache, no-store, must-revalidate'
                }
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Error getting recent watchlist:', errorData);
                throw new Error(`Nie udało się pobrać ostatnich filmów z listy do obejrzenia: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Network error getting recent watchlist:', error);
            throw error;
        }
    }
}

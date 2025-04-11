export class FavoriteMovieService {
    static async addToFavorites(movieId: number, token: string): Promise<void> {
        const response = await fetch(`http://localhost:5000/api/favorites/add`, {
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
            throw new Error(`Nie udało się dodać do ulubionych: ${response.status}`);
        }
    }

    static async removeFromFavorites(movieId: number, token: string): Promise<void> {
        const response = await fetch(`http://localhost:5000/api/favorites/remove?movie_id=${movieId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się usunąć z ulubionych: ${response.status}`);
        }
    }

    static async checkIfFavorite(movieId: number, token: string): Promise<boolean> {
        const response = await fetch(`http://localhost:5000/api/favorites/check/${movieId}`, {
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
        return data.is_favorite ?? false;
    }

    static async getUserFavorites(token: string, page: number = 1, perPage: number = 10): Promise<any> {
        const response = await fetch(`http://localhost:5000/api/favorites/user?page=${page}&per_page=${perPage}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się pobrać ulubionych: ${response.status}`);
        }

        return await response.json();
    }

    static async getMovieFavoriteCount(movieId: number): Promise<number> {
        const response = await fetch(`http://localhost:5000/api/favorites/count/${movieId}`);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Nie udało się pobrać liczby polubień: ${response.status}`);
        }

        const data = await response.json();
        return data.count ?? 0;
    }
}

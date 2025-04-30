import { fetchWithAuth } from '../../../services/api';

export class FavoriteMovieService {
    static async addToFavorites(movieId: number): Promise<void> {
        await fetchWithAuth('favorites/add', {
            method: 'POST',
            body: JSON.stringify({ movie_id: movieId }),
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    static async removeFromFavorites(movieId: number): Promise<void> {
        await fetchWithAuth(`favorites/remove?movie_id=${movieId}`, {
            method: 'DELETE'
        });
    }

    static async checkIfFavorite(movieId: number): Promise<boolean> {
        const data = await fetchWithAuth(`favorites/check/${movieId}`);
        return data.is_favorite ?? false;
    }

    static async getUserFavorites(page: number = 1, perPage: number = 10): Promise<any> {
        return fetchWithAuth(`favorites/user?page=${page}&per_page=${perPage}`);
    }

    static async getMovieFavoriteCount(movieId: number): Promise<number> {
        const data = await fetchWithAuth(`favorites/count/${movieId}`);
        return data.count ?? 0;
    }
}

import { fetchWithAuth } from '../../../services/api';

export class RatingService {
    static async fetchUserRating(movieId: number): Promise<number> {
        const response = await fetchWithAuth(`ratings/movies/${movieId}/user-rating`);
        return response.rating ?? 0;
    }

    static async submitRating(movieId: number, rating: number): Promise<void> {
        await fetchWithAuth(`ratings/movies/${movieId}/user-rating`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rating })
        });
    }

    static async deleteRating(movieId: number): Promise<void> {
        await fetchWithAuth(`ratings/movies/${movieId}/user-rating`, {
            method: 'DELETE'
        });
    }
}

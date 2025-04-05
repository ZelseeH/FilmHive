export class RatingService {
    static async fetchUserRating(movieId: number, token: string): Promise<number> {
        const response = await fetch(`http://localhost:5000/api/ratings/movies/${movieId}/user-rating`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) throw new Error(`Nie udało się pobrać oceny: ${response.status}`);

        const data = await response.json();
        return data.rating ?? 0; // Ensure rating is returned as a number
    }

    static async submitRating(movieId: number, rating: number, token: string): Promise<void> {
        if (!token) throw new Error('Musisz być zalogowany, aby ocenić film');

        const response = await fetch(`http://localhost:5000/api/ratings/movies/${movieId}/ratings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ rating })
        });

        if (!response.ok) throw new Error('Wystąpił błąd podczas oceniania filmu');
    }
}

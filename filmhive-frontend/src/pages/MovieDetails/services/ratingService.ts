export class RatingService {
    // Pomocnicza metoda do sprawdzania czy film już wyszedł
    private static isMovieReleased(releaseDate?: string): boolean {
        if (!releaseDate) return true;
        const release = new Date(releaseDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return release <= today;
    }

    static async fetchUserRating(movieId: number, token: string, releaseDate?: string): Promise<number> {
        // Jeśli film nie wyszedł, zwróć 0 bez sprawdzania backendu
        if (!this.isMovieReleased(releaseDate)) {
            return 0;
        }

        const response = await fetch(`http://localhost:5000/api/ratings/movies/${movieId}/user-rating`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) throw new Error(`Nie udało się pobrać oceny: ${response.status}`);

        const data = await response.json();
        return data.rating ?? 0;
    }

    static async submitRating(movieId: number, rating: number, token: string, releaseDate?: string): Promise<void> {
        if (!token) throw new Error('Musisz być zalogowany, aby ocenić film');

        // TYLKO TUTAJ sprawdź datę premiery przed DODANIEM oceny
        if (!this.isMovieReleased(releaseDate)) {
            throw new Error('Nie można ocenić filmu, który jeszcze nie miał premiery');
        }

        const response = await fetch(`http://localhost:5000/api/ratings/movies/${movieId}/ratings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ rating })
        });

        if (!response.ok) {
            try {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Wystąpił błąd podczas oceniania filmu');
            } catch (parseError) {
                throw new Error('Wystąpił błąd podczas oceniania filmu');
            }
        }
    }

    static async deleteRating(movieId: number, token: string, releaseDate?: string): Promise<void> {
        if (!token) throw new Error('Musisz być zalogowany, aby usunąć ocenę');

        // NIE SPRAWDZAJ daty premiery przy usuwaniu - pozwól usunąć istniejącą ocenę

        const response = await fetch(`http://localhost:5000/api/ratings/movies/${movieId}/user-rating`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            try {
                const errorData = await response.json();
                throw new Error(errorData.error || `Nie udało się usunąć oceny: ${response.status}`);
            } catch (parseError) {
                throw new Error(`Nie udało się usunąć oceny: ${response.status}`);
            }
        }
    }
}

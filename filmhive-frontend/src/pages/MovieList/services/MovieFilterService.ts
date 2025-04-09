// src/pages/services/MovieFilterService.ts
const MovieFilterService = {
    async getGenres(): Promise<{ id: number, name: string }[]> {
        try {
            const response = await fetch('/api/genres');
            if (!response.ok) {
                throw new Error('Failed to fetch genres');
            }
            const data = await response.json();
            return data || [];
        } catch (error) {
            console.error('Error in getGenres:', error);
            throw error;
        }
    },

    async getCountries(): Promise<string[]> {
        try {
            const response = await fetch('/api/movies/filter-options');
            if (!response.ok) {
                throw new Error('Failed to fetch filter options');
            }
            const data = await response.json();
            return data.countries || [];
        } catch (error) {
            console.error('Error in getCountries:', error);
            throw error;
        }
    }
};

export default MovieFilterService;

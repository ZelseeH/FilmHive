import { fetchWithAuth } from '../../../services/api';

const ActorFilterService = {
    async getBirthplaces(): Promise<string[]> {
        try {
            // Jeśli endpoint wymaga autoryzacji, użyj fetchWithAuth
            const data = await fetchWithAuth('actors/birthplaces');
            // Marshmallow zwraca { birthplaces: [...] }
            return data.birthplaces || [];
        } catch (error: any) {
            console.error('Error in getBirthplaces:', error);
            throw new Error(error.message || 'Błąd podczas pobierania miejsc urodzenia');
        }
    }
};

export default ActorFilterService;

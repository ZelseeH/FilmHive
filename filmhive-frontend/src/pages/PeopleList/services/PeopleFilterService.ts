const API_URL = 'http://localhost:5000/api/people';

const PeopleFilterService = {
    async getBirthplaces(type: 'actor' | 'director' = 'actor'): Promise<string[]> {
        try {
            const response = await fetch(`${API_URL}/birthplaces?type=${type}`);
            if (!response.ok) {
                throw new Error('Failed to fetch birthplaces');
            }
            const data = await response.json();
            return data.birthplaces || [];
        } catch (error) {
            console.error('Error in getBirthplaces:', error);
            throw error;
        }
    }
};

export default PeopleFilterService;

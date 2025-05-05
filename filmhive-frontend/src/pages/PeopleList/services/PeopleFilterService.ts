const PeopleFilterService = {
    async getBirthplaces(): Promise<string[]> {
        try {
            const response = await fetch('http://localhost:5000/api/people/birthplaces');
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

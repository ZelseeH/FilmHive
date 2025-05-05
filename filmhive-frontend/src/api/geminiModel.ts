// api/geminiModel.ts
export const generateContent = async (prompt: string): Promise<string> => {
    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: prompt }),
        });

        if (!response.ok) {
            throw new Error('Błąd komunikacji z serwerem');
        }

        const data = await response.json();
        return data.answer;
    } catch (error) {
        console.error("API error:", error);
        return "Wystąpił błąd podczas przetwarzania zapytania";
    }
};

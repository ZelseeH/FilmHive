import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { generateContent } from '../../api/geminiModel';
import styles from './GeminiChatbot.module.css';

interface ChatMessage {
    content: string;
    isBot: boolean;
}

const GeminiChatbot: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [inputMessage, setInputMessage] = useState('');
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [showWelcome, setShowWelcome] = useState(true);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const isFilmRelated = (query: string): boolean => {
        const filmKeywords = [
            'film', 'filmy', 'akcja', 'kino', 'aktor', 'aktorka', 'reżyser', 'scenariusz', 'scenarzysta',
            'premiera', 'obsada', 'serial', 'seriale', 'sezon', 'odcinek', 'odcinki',
            'postać', 'postacie', 'rola', 'role', 'nagroda', 'nagrody', 'oscar', 'oscary',
            'kamera', 'montaż', 'efekty', 'specjalne efekty', 'box office', 'bilety',
            'krytycy', 'recenzja', 'recenzje', 'gatunek', 'gatunki', 'komedia', 'dramat',
            'horror', 'thriller', 'sci-fi', 'science fiction', 'fantasy', 'animacja',
            'film animowany', 'dokument', 'dokumentalny', 'soundtrack', 'muzyka filmowa',
            'zwiastun', 'trailer', 'produkcja', 'studio', 'wytwórnia', 'hollywood',
            'kaskader', 'scenografia', 'kostiumy', 'charakteryzacja', 'nominacja',
            'festiwal', 'festiwale', 'kinematografia', 'operator', 'zdjęcia', 'netflix',
            'hbo', 'disney', 'disney+', 'amazon', 'prime video', 'streaming', 'vod',
            'kino domowe', 'plakat', 'plakaty filmowe', 'napisy', 'lektor', 'dubbing',
            'wydanie dvd', 'bluray', 'premiera kinowa', 'premiera telewizyjna', 'marvel',
            'dc', 'pixar', 'dreamworks', 'studio ghibli', 'biografia filmowa', 'remake',
            'reboot', 'spin-off', 'kontynuacja', 'adaptacja', 'book to movie', 'film akcji',
            'film przygodowy', 'film wojenny', 'film romantyczny', 'film historyczny',
            'serial kryminalny', 'miniserial', 'limited series'
        ];

        const lowerCaseQuery = query.toLowerCase();
        return filmKeywords.some(keyword => lowerCaseQuery.includes(keyword));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputMessage.trim() || isLoading) return;

        setShowWelcome(false);
        const userMessage = { content: inputMessage, isBot: false };
        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            const isFirstUserMessage = messages.filter(m => !m.isBot).length === 0;

            if (isFirstUserMessage && !isFilmRelated(inputMessage)) {
                setMessages(prev => [...prev, {
                    content: "Przepraszam, ale mogę odpowiadać tylko na pytania związane z filmami, kinem, aktorami i serialami. Czy mogę pomóc Ci w znalezieniu informacji na temat świata filmu?",
                    isBot: true
                }]);
                setIsLoading(false);
                return;
            }


            let contextualPrompt = `Jesteś asystentem filmowym FilmHive. Odpowiadaj WYŁĄCZNIE na tematy związane z filmami, serialami, aktorami, reżyserami i kinem.`;

            const recentMessages = messages.slice(-10);
            if (recentMessages.length > 0) {
                contextualPrompt += `\n\nHistoria konwersacji:`;
                recentMessages.forEach(m => {
                    contextualPrompt += `\n${m.isBot ? 'Ty' : 'Użytkownik'}: ${m.content}`;
                });
            }

            contextualPrompt += `\n\nNowe pytanie użytkownika: ${inputMessage}\n\nOdpowiedz jako FilmHive Assistant:`;

            const botResponse = await generateContent(contextualPrompt);
            setMessages(prev => [...prev, { content: botResponse, isBot: true }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                content: "Wystąpił błąd podczas komunikacji z serwerem",
                isBot: true
            }]);
        }

        setIsLoading(false);
    };

    return (
        <div className={styles.chatbotContainer}>
            <button
                className={styles.toggleButton}
                onClick={() => setIsOpen(!isOpen)}
                aria-label="Otwórz/zamknij czat"
            >
                {isOpen ? '×' : '💬'}
            </button>

            {isOpen && (
                <div className={styles.chatWindow}>
                    <div className={styles.header}>
                        FilmHive Assistant
                    </div>
                    <div className={styles.messagesContainer}>
                        {showWelcome && messages.length === 0 && (
                            <div className={styles.welcomeMessage}>
                                <p>Witaj w FilmHive Assistant! 👋</p>
                                <p>Możesz zapytać mnie o:</p>
                                <ul>
                                    <li>Informacje o filmach i serialach</li>
                                    <li>Biografie aktorów i reżyserów</li>
                                    <li>Rekomendacje filmów podobnych do twoich ulubionych</li>
                                    <li>Nowości kinowe i nadchodzące premiery</li>
                                </ul>
                            </div>
                        )}
                        {messages.map((message, index) => (
                            <div
                                key={index}
                                className={`${styles.message} ${message.isBot ? styles.bot : styles.user}`}
                            >
                                <div className={styles.markdown}>
                                    <ReactMarkdown>{message.content}</ReactMarkdown>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className={styles.loadingDots}>
                                <div className={styles.dot}></div>
                                <div className={styles.dot}></div>
                                <div className={styles.dot}></div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                    <form onSubmit={handleSubmit} className={styles.inputForm}>
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder="Zapytaj o filmy lub aktorów..."
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={isLoading}
                            className={styles.sendButton}
                        >
                            Wyślij
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default GeminiChatbot;

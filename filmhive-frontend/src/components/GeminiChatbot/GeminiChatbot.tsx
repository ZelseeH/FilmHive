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

    // Lista słów kluczowych związanych z filmem i kinem
    const isFilmRelated = (query: string): boolean => {
        const filmKeywords = [
            'film', 'kino', 'aktor', 'reżyser', 'scenariusz', 'premiera', 'obsada',
            'serial', 'postać', 'rola', 'nagroda', 'oscar', 'kamera', 'montaż',
            'efekty', 'box office', 'bilety', 'krytycy', 'recenzja', 'gatunek',
            'komedia', 'dramat', 'horror', 'thriller', 'sci-fi', 'fantasy',
            'animacja', 'dokument', 'soundtrack', 'muzyka', 'zwiastun', 'trailer',
            'produkcja', 'studio', 'hollywood', 'kaskader', 'scenografia', 'kostiumy',
            'charakteryzacja', 'nominacja', 'festiwal', 'kinematografia', 'operator',
            'netflix', 'hbo', 'disney', 'amazon', 'streaming', 'vod', 'kamera'
        ];

        const lowercaseQuery = query.toLowerCase();
        return filmKeywords.some(keyword => lowercaseQuery.includes(keyword));
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
            // Sprawdź, czy pytanie dotyczy filmów
            if (!isFilmRelated(inputMessage)) {
                setMessages(prev => [...prev, {
                    content: "Przepraszam, ale mogę odpowiadać tylko na pytania związane z filmami, kinem, aktorami i serialami. Czy mogę pomóc Ci w znalezieniu informacji na temat świata filmu?",
                    isBot: true
                }]);
                setIsLoading(false);
                return;
            }

            // Dodaj kontekst do zapytania
            const contextualPrompt = `Kontekst: Jesteś asystentem filmowym FilmHive, który odpowiada WYŁĄCZNIE na pytania związane z filmami, serialami, aktorami, reżyserami i światem kina. Pytanie użytkownika: ${inputMessage}`;

            const botResponse = await generateContent(contextualPrompt);
            setMessages(prev => [...prev, { content: botResponse, isBot: true }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                content: "Wystąpił błąd podczas komunikacji z AI",
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
                                <p>• Informacje o filmach i serialach</p>
                                <p>• Biografie aktorów i reżyserów</p>
                                <p>• Rekomendacje filmów podobnych do twoich ulubionych</p>
                                <p>• Nowości kinowe i nadchodzące premiery</p>
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

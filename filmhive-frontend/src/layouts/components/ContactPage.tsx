import React, { useState, ChangeEvent, FormEvent } from 'react';
import styles from './ContactPage.module.css';

interface FormData {
    name: string;
    email: string;
    subject: string;
    message: string;
}

const ContactPage: React.FC = () => {
    const [formData, setFormData] = useState<FormData>({
        name: '',
        email: '',
        subject: '',
        message: ''
    });

    const [submitted, setSubmitted] = useState<boolean>(false);

    const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        // Tutaj dodałbyś logikę wysyłania formularza
        console.log('Form submitted:', formData);
        setSubmitted(true);

        // Reset formularza po wysłaniu
        setTimeout(() => {
            setFormData({
                name: '',
                email: '',
                subject: '',
                message: ''
            });
            setSubmitted(false);
        }, 3000);
    };

    return (
        <div className={styles.container}>
            <div className={styles.pageHeader}>
                <h1 className={styles.pageTitle}>Kontakt</h1>
                <div className={styles.titleUnderline}></div>
            </div>

            <div className={styles.contactWrapper}>
                <div className={styles.contactInfo}>
                    <h2 className={styles.sectionTitle}>Skontaktuj się z nami</h2>
                    <p className={styles.paragraph}>
                        Masz pytania, sugestie lub potrzebujesz pomocy? Wypełnij formularz lub skorzystaj z poniższych danych kontaktowych.
                    </p>

                    <div className={styles.infoItem}>
                        <div className={styles.infoIcon}>📧</div>
                        <div className={styles.infoContent}>
                            <h3 className={styles.infoTitle}>Email</h3>
                            <p className={styles.infoText}>kontakt@filmhive.pl</p>
                        </div>
                    </div>

                    <div className={styles.infoItem}>
                        <div className={styles.infoIcon}>📱</div>
                        <div className={styles.infoContent}>
                            <h3 className={styles.infoTitle}>Telefon</h3>
                            <p className={styles.infoText}>+48 123 456 789</p>
                        </div>
                    </div>

                    <div className={styles.infoItem}>
                        <div className={styles.infoIcon}>🏢</div>
                        <div className={styles.infoContent}>
                            <h3 className={styles.infoTitle}>Adres</h3>
                            <p className={styles.infoText}>ul. Filmowa 123<br />00-001 Warszawa</p>
                        </div>
                    </div>

                    <div className={styles.socialLinks}>
                        <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" className={styles.socialLink}>Facebook</a>
                        <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className={styles.socialLink}>Twitter</a>
                        <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" className={styles.socialLink}>Instagram</a>
                    </div>
                </div>

                <div className={styles.contactForm}>
                    {submitted ? (
                        <div className={styles.successMessage}>
                            <h3>Dziękujemy za wiadomość!</h3>
                            <p>Odpowiemy najszybciej jak to możliwe.</p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit}>
                            <div className={styles.formGroup}>
                                <label htmlFor="name" className={styles.formLabel}>Imię i nazwisko</label>
                                <input
                                    type="text"
                                    id="name"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className={styles.formInput}
                                    required
                                />
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="email" className={styles.formLabel}>Email</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className={styles.formInput}
                                    required
                                />
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="subject" className={styles.formLabel}>Temat</label>
                                <input
                                    type="text"
                                    id="subject"
                                    name="subject"
                                    value={formData.subject}
                                    onChange={handleChange}
                                    className={styles.formInput}
                                    required
                                />
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="message" className={styles.formLabel}>Wiadomość</label>
                                <textarea
                                    id="message"
                                    name="message"
                                    value={formData.message}
                                    onChange={handleChange}
                                    className={styles.formTextarea}
                                    rows={6}
                                    required
                                ></textarea>
                            </div>

                            <button type="submit" className={styles.submitButton}>Wyślij wiadomość</button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ContactPage;

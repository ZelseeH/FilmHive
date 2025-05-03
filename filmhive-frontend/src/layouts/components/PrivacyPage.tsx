import React from 'react';
import styles from './PrivacyPage.module.css';

const PrivacyPage = () => {
    return (
        <div className={styles.container}>
            <div className={styles.pageHeader}>
                <h1 className={styles.pageTitle}>Polityka prywatności</h1>
                <div className={styles.titleUnderline}></div>
            </div>

            <div className={styles.privacyContent}>
                <p className={styles.lastUpdated}>Ostatnia aktualizacja: 1 maja 2025 r.</p>

                <section className={styles.privacySection}>
                    <h2 className={styles.sectionTitle}>1. Wprowadzenie</h2>
                    <p className={styles.paragraph}>
                        Niniejsza Polityka Prywatności określa zasady przetwarzania i ochrony danych osobowych użytkowników serwisu FilmHive. Administratorem danych osobowych jest FilmHive Sp. z o.o. z siedzibą w Warszawie.
                    </p>
                    <p className={styles.paragraph}>
                        Szanujemy prawo do prywatności i dbamy o bezpieczeństwo danych. Dane osobowe są przetwarzane zgodnie z Rozporządzeniem Parlamentu Europejskiego i Rady (UE) 2016/679 z dnia 27 kwietnia 2016 r. (RODO) oraz innymi obowiązującymi przepisami prawa.
                    </p>
                </section>

                <section className={styles.privacySection}>
                    <h2 className={styles.sectionTitle}>2. Jakie dane zbieramy</h2>
                    <p className={styles.paragraph}>
                        W zależności od sposobu korzystania z Serwisu, możemy zbierać następujące dane:
                    </p>
                    <ul className={styles.privacyList}>
                        <li><strong>Dane podawane podczas rejestracji:</strong> imię, nazwisko, adres e-mail, nazwa użytkownika</li>
                        <li><strong>Dane podawane dobrowolnie w profilu:</strong> zdjęcie profilowe, data urodzenia, płeć, lokalizacja</li>
                        <li><strong>Dane o aktywności:</strong> oceny filmów, komentarze, listy filmów, interakcje z innymi użytkownikami</li>
                        <li><strong>Dane techniczne:</strong> adres IP, informacje o urządzeniu, przeglądarce, czasie spędzonym w Serwisie</li>
                    </ul>
                </section>

                <section className={styles.privacySection}>
                    <h2 className={styles.sectionTitle}>3. Cele przetwarzania danych</h2>
                    <p className={styles.paragraph}>
                        Dane osobowe Użytkowników przetwarzamy w następujących celach:
                    </p>
                    <ul className={styles.privacyList}>
                        <li>Świadczenie usług w ramach Serwisu, w tym tworzenie i zarządzanie kontem użytkownika</li>
                        <li>Dostarczanie spersonalizowanych rekomendacji filmowych</li>
                        <li>Komunikacja z Użytkownikami, w tym odpowiadanie na zapytania i zgłoszenia</li>
                        <li>Poprawa jakości usług i rozwój nowych funkcjonalności</li>
                        <li>Zapewnienie bezpieczeństwa Serwisu i przeciwdziałanie nadużyciom</li>
                        <li>Prowadzenie analiz statystycznych</li>
                        <li>Marketing własnych usług (w przypadku wyrażenia zgody)</li>
                    </ul>
                </section>

                <section className={styles.privacySection}>
                    <h2 className={styles.sectionTitle}>4. Podstawy prawne przetwarzania</h2>
                    <p className={styles.paragraph}>
                        Przetwarzamy dane osobowe na następujących podstawach prawnych:
                    </p>
                    <ul className={styles.privacyList}>
                        <li>Wykonanie umowy (art. 6 ust. 1 lit. b RODO) - w zakresie niezbędnym do świadczenia usług</li>
                        <li>Prawnie uzasadniony interes administratora (art. 6 ust. 1 lit. f RODO) - w zakresie analityki, poprawy jakości usług, bezpieczeństwa</li>
                        <li>Zgoda Użytkownika (art. 6 ust. 1 lit. a RODO) - w zakresie marketingu, cookies niezbędnych do funkcjonowania serwisu</li>
                        <li>Obowiązek prawny (art. 6 ust. 1 lit. c RODO) - w zakresie wynikającym z przepisów prawa</li>
                    </ul>
                </section>

                <section className={styles.privacySection}>
                    <h2 className={styles.sectionTitle}>5. Udostępnianie danych</h2>
                    <p className={styles.paragraph}>
                        Dane osobowe Użytkowników mogą być udostępniane następującym kategoriom odbiorców:
                    </p>
                    <ul className={styles.privacyList}>
                        <li>Podmioty przetwarzające dane na nasze zlecenie, np. dostawcy usług IT, hostingowych, analitycznych</li>
                        <li>Podmioty uprawnione na podstawie przepisów prawa, np. organy państwowe</li>
                        <li>Partnerzy biznesowi (wyłącznie za zgodą Użytkownika)</li>
                    </ul>
                    <p className={styles.paragraph}>
                        Nie sprzedajemy danych osobowych Użytkowników.
                    </p>
                </section>

                <section className={styles.privacySection}>
                    <h2 className={styles.sectionTitle}>6. Prawa Użytkowników</h2>
                    <p className={styles.paragraph}>
                        Każdy Użytkownik ma prawo do:
                    </p>
                    <ul className={styles.privacyList}>
                        <li>Dostępu do swoich danych oraz otrzymania ich kopii</li>
                        <li>Sprostowania (poprawiania) swoich danych</li>
                        <li>Usunięcia danych (prawo do bycia zapomnianym)</li>
                        <li>Ograniczenia przetwarzania danych</li>
                        <li>Przenoszenia danych</li>
                        <li>Sprzeciwu wobec przetwarzania danych</li>
                        <li>Cofnięcia zgody w dowolnym momencie (bez wpływu na zgodność z prawem przetwarzania dokonanego przed cofnięciem zgody)</li>
                        <li>Wniesienia skargi do organu nadzorczego</li>
                    </ul>
                </section>

                <section className={styles.privacySection}>
                    <h2 className={styles.sectionTitle}>7. Okres przechowywania danych</h2>
                    <p className={styles.paragraph}>
                        Dane osobowe Użytkowników przechowujemy przez okres:
                    </p>
                    <ul className={styles.privacyList}>
                        <li>Aktywności konta w Serwisie</li>
                        <li>Niezbędny do realizacji celów, dla których zostały zebrane</li>
                        <li>Wynikający z przepisów prawa (np. przepisy podatkowe, archiwizacyjne)</li>
                        <li>Do czasu cofnięcia zgody (jeśli podstawą przetwarzania jest zgoda)</li>
                    </ul>
                    <p className={styles.paragraph}>
                        Po upływie okresu przechowywania dane są usuwane lub anonimizowane.
                    </p>
                </section>

                <section className={styles.privacySection}>
                    <h2 className={styles.sectionTitle}>8. Bezpieczeństwo danych</h2>
                    <p className={styles.paragraph}>
                        Stosujemy odpowiednie środki techniczne i organizacyjne, aby zapewnić bezpieczeństwo danych osobowych, w tym:
                    </p>
                    <ul className={styles.privacyList}>
                        <li>Szyfrowanie danych (protokół SSL)</li>
                        <li>Regularne testy bezpieczeństwa</li>
                        <li>Kontrolę dostępu do danych</li>
                        <li>Szkolenia personelu</li>
                        <li>Procedury reagowania na incydenty bezpieczeństwa</li>
                    </ul>
                </section>

                <section className={styles.privacySection}>
                    <h2 className={styles.sectionTitle}>9. Kontakt</h2>
                    <p className={styles.paragraph}>
                        W sprawach związanych z ochroną danych osobowych można kontaktować się z naszym Inspektorem Ochrony Danych:
                    </p>
                    <p className={styles.paragraph}>
                        Email: iod@filmhive.pl<br />
                        Adres: ul. Filmowa 123, 00-001 Warszawa
                    </p>
                </section>
            </div>
        </div>
    );
};

export default PrivacyPage;

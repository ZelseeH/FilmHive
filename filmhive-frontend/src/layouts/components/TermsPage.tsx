import React from 'react';
import styles from './TermsPage.module.css';

const TermsPage = () => {
    return (
        <div className={styles.container}>
            <div className={styles.pageHeader}>
                <h1 className={styles.pageTitle}>Regulamin serwisu</h1>
                <div className={styles.titleUnderline}></div>
            </div>

            <div className={styles.termsContent}>
                <p className={styles.lastUpdated}>Ostatnia aktualizacja: 1 maja 2025 r.</p>

                <section className={styles.termsSection}>
                    <h2 className={styles.sectionTitle}>1. Postanowienia ogólne</h2>
                    <p className={styles.paragraph}>
                        Niniejszy Regulamin określa warunki korzystania z serwisu internetowego FilmHive, dostępnego pod adresem www.filmhive.pl. Korzystanie z Serwisu oznacza akceptację niniejszego Regulaminu.
                    </p>
                    <p className={styles.paragraph}>
                        Właścicielem Serwisu jest FilmHive Sp. z o.o. z siedzibą w Warszawie, ul. Filmowa 123, 00-001 Warszawa, wpisana do rejestru przedsiębiorców Krajowego Rejestru Sądowego pod numerem KRS 0000000000.
                    </p>
                </section>

                <section className={styles.termsSection}>
                    <h2 className={styles.sectionTitle}>2. Definicje</h2>
                    <p className={styles.paragraph}>
                        <strong>Serwis</strong> - serwis internetowy FilmHive dostępny pod adresem www.filmhive.pl<br />
                        <strong>Użytkownik</strong> - osoba fizyczna korzystająca z Serwisu<br />
                        <strong>Konto</strong> - zbiór zasobów i uprawnień w ramach Serwisu przypisanych konkretnemu Użytkownikowi<br />
                        <strong>Treści</strong> - wszelkie materiały, w tym teksty, zdjęcia, filmy, grafiki, komentarze, oceny i inne materiały zamieszczane przez Użytkownika w Serwisie
                    </p>
                </section>

                <section className={styles.termsSection}>
                    <h2 className={styles.sectionTitle}>3. Zasady korzystania z Serwisu</h2>
                    <p className={styles.paragraph}>
                        Korzystanie z Serwisu jest dobrowolne i bezpłatne. Niektóre funkcje Serwisu mogą być dostępne wyłącznie dla zarejestrowanych Użytkowników.
                    </p>
                    <p className={styles.paragraph}>
                        Użytkownik zobowiązuje się do korzystania z Serwisu zgodnie z obowiązującymi przepisami prawa, normami społecznymi i obyczajowymi oraz postanowieniami niniejszego Regulaminu.
                    </p>
                    <p className={styles.paragraph}>
                        Zabronione jest:
                    </p>
                    <ul className={styles.termsList}>
                        <li>Publikowanie treści naruszających prawo, dobra osobiste osób trzecich lub sprzecznych z dobrymi obyczajami</li>
                        <li>Wykorzystywanie Serwisu do publikowania reklam lub innych treści o charakterze komercyjnym</li>
                        <li>Podejmowanie działań mających na celu destabilizację pracy Serwisu</li>
                        <li>Próby uzyskania dostępu do danych innych Użytkowników</li>
                    </ul>
                </section>

                <section className={styles.termsSection}>
                    <h2 className={styles.sectionTitle}>4. Rejestracja i konto Użytkownika</h2>
                    <p className={styles.paragraph}>
                        Rejestracja w Serwisie jest dobrowolna i bezpłatna. W celu rejestracji należy wypełnić formularz rejestracyjny, podając wymagane dane oraz akceptując Regulamin i Politykę Prywatności.
                    </p>
                    <p className={styles.paragraph}>
                        Użytkownik jest odpowiedzialny za zachowanie poufności swojego hasła i zobowiązuje się do nieudostępniania go osobom trzecim.
                    </p>
                </section>

                <section className={styles.termsSection}>
                    <h2 className={styles.sectionTitle}>5. Prawa autorskie</h2>
                    <p className={styles.paragraph}>
                        Serwis oraz wszystkie zawarte w nim treści, takie jak teksty, grafiki, logotypy, zdjęcia, filmy, układ witryny i inne, są chronione prawem autorskim.
                    </p>
                    <p className={styles.paragraph}>
                        Użytkownik, publikując jakiekolwiek Treści w Serwisie, udziela Serwisowi niewyłącznej, bezpłatnej licencji na korzystanie, utrwalanie, przechowywanie i udostępnianie tych Treści w ramach Serwisu.
                    </p>
                </section>

                <section className={styles.termsSection}>
                    <h2 className={styles.sectionTitle}>6. Odpowiedzialność</h2>
                    <p className={styles.paragraph}>
                        Serwis nie ponosi odpowiedzialności za treści publikowane przez Użytkowników. Użytkownik ponosi pełną odpowiedzialność za publikowane przez siebie Treści.
                    </p>
                    <p className={styles.paragraph}>
                        Serwis zastrzega sobie prawo do moderowania, edytowania lub usuwania Treści naruszających niniejszy Regulamin lub przepisy prawa.
                    </p>
                </section>

                <section className={styles.termsSection}>
                    <h2 className={styles.sectionTitle}>7. Postanowienia końcowe</h2>
                    <p className={styles.paragraph}>
                        Serwis zastrzega sobie prawo do zmiany niniejszego Regulaminu. Zmiany wchodzą w życie po upływie 7 dni od dnia ich opublikowania w Serwisie.
                    </p>
                    <p className={styles.paragraph}>
                        W sprawach nieuregulowanych niniejszym Regulaminem zastosowanie mają przepisy prawa polskiego.
                    </p>
                </section>
            </div>
        </div>
    );
};

export default TermsPage;

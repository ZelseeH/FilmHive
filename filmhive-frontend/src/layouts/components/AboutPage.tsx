import React from 'react';
import styles from './AboutPage.module.css';
import filmhiveImg from './filmhive.png';

const AboutPage = () => {
    return (
        <div className={styles.container}>
            <div className={styles.pageHeader}>
                <h1 className={styles.pageTitle}>O nas</h1>
                <div className={styles.titleUnderline}></div>
            </div>

            <section className={styles.aboutSection}>
                <div className={styles.aboutContent}>
                    <h2 className={styles.sectionTitle}>Nasza historia</h2>
                    <p className={styles.paragraph}>
                        FilmHive powstało w 2023 roku z pasji do kina i chęci stworzenia miejsca, gdzie miłośnicy filmów mogą dzielić się swoimi opiniami, odkrywać nowe tytuły i budować społeczność kinomaniaków. Naszym celem jest dostarczanie użytkownikom najlepszych rekomendacji filmowych dopasowanych do ich indywidualnych preferencji.
                    </p>

                    <div className={styles.imageContainer}>
                        <img src={filmhiveImg} alt="Zespół FilmHive" className={styles.teamImage} />
                    </div>

                    <h2 className={styles.sectionTitle}>Nasza misja</h2>
                    <p className={styles.paragraph}>
                        Wierzymy, że filmy mają moc łączenia ludzi i inspirowania do nowych pomysłów. Dlatego tworzymy platformę, która nie tylko pomaga w odkrywaniu filmów, ale również buduje społeczność pasjonatów kina z całego świata.
                    </p>

                    <div className={styles.valuesContainer}>
                        <div className={styles.valueCard}>
                            <div className={styles.valueIcon}>🎬</div>
                            <h3 className={styles.valueTitle}>Pasja do kina</h3>
                            <p className={styles.valueDescription}>Kochamy filmy i chcemy dzielić się tą pasją z innymi.</p>
                        </div>

                        <div className={styles.valueCard}>
                            <div className={styles.valueIcon}>👥</div>
                            <h3 className={styles.valueTitle}>Społeczność</h3>
                            <p className={styles.valueDescription}>Budujemy miejsce, gdzie każdy kinoman czuje się jak w domu.</p>
                        </div>

                        <div className={styles.valueCard}>
                            <div className={styles.valueIcon}>💡</div>
                            <h3 className={styles.valueTitle}>Innowacja</h3>
                            <p className={styles.valueDescription}>Stale rozwijamy nasze algorytmy rekomendacji, aby dostarczać najlepsze sugestie.</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default AboutPage;

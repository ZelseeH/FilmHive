import React, { useState, useEffect } from 'react';
import { useTheme } from '../../../../contexts/ThemeContext';
import styles from './SettingsPage.module.css';

const SettingsPage: React.FC = () => {
    const { isDarkMode, setTheme } = useTheme();
    const [siteName, setSiteName] = useState<string>('FilmHive');
    const [language, setLanguage] = useState<string>('pl');
    const [itemsPerPage, setItemsPerPage] = useState<number>(20);
    const [autoSave, setAutoSave] = useState<boolean>(true);
    const [showTutorials, setShowTutorials] = useState<boolean>(true);
    const [compactMode, setCompactMode] = useState<boolean>(false);

    // Załaduj ustawienia z localStorage przy starcie
    useEffect(() => {
        const savedSiteName = localStorage.getItem('siteName');
        const savedLanguage = localStorage.getItem('language');
        const savedItemsPerPage = localStorage.getItem('itemsPerPage');
        const savedAutoSave = localStorage.getItem('autoSave');
        const savedShowTutorials = localStorage.getItem('showTutorials');
        const savedCompactMode = localStorage.getItem('compactMode');

        if (savedSiteName) setSiteName(savedSiteName);
        if (savedLanguage) setLanguage(savedLanguage);
        if (savedItemsPerPage) setItemsPerPage(parseInt(savedItemsPerPage));
        if (savedAutoSave) setAutoSave(savedAutoSave === 'true');
        if (savedShowTutorials) setShowTutorials(savedShowTutorials === 'true');
        if (savedCompactMode) setCompactMode(savedCompactMode === 'true');
    }, []);

    const handleThemeChange = (dark: boolean) => {
        setTheme(dark);
    };

    const handleSave = () => {
        localStorage.setItem('siteName', siteName);
        localStorage.setItem('language', language);
        localStorage.setItem('itemsPerPage', itemsPerPage.toString());
        localStorage.setItem('autoSave', autoSave.toString());
        localStorage.setItem('showTutorials', showTutorials.toString());
        localStorage.setItem('compactMode', compactMode.toString());

        alert('Ustawienia zostały zapisane!');
    };

    const handleReset = () => {
        if (window.confirm('Czy na pewno chcesz przywrócić domyślne ustawienia?')) {
            setTheme(false);
            setSiteName('FilmHive');
            setLanguage('pl');
            setItemsPerPage(20);
            setAutoSave(true);
            setShowTutorials(true);
            setCompactMode(false);

            localStorage.removeItem('siteName');
            localStorage.removeItem('language');
            localStorage.removeItem('itemsPerPage');
            localStorage.removeItem('autoSave');
            localStorage.removeItem('showTutorials');
            localStorage.removeItem('compactMode');

            alert('Ustawienia zostały przywrócone do domyślnych!');
        }
    };

    const handleExportSettings = () => {
        const settings = {
            siteName,
            language,
            itemsPerPage,
            autoSave,
            showTutorials,
            compactMode,
            theme: isDarkMode ? 'dark' : 'light',
            exportDate: new Date().toISOString()
        };

        const dataStr = JSON.stringify(settings, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

        const exportFileDefaultName = `filmhive-settings-${new Date().toISOString().split('T')[0]}.json`;

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    };

    const handleImportSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const settings = JSON.parse(e.target?.result as string);

                if (settings.siteName) setSiteName(settings.siteName);
                if (settings.language) setLanguage(settings.language);
                if (settings.itemsPerPage) setItemsPerPage(settings.itemsPerPage);
                if (typeof settings.autoSave === 'boolean') setAutoSave(settings.autoSave);
                if (typeof settings.showTutorials === 'boolean') setShowTutorials(settings.showTutorials);
                if (typeof settings.compactMode === 'boolean') setCompactMode(settings.compactMode);
                if (settings.theme) setTheme(settings.theme === 'dark');

                alert('Ustawienia zostały zaimportowane!');
            } catch (error) {
                alert('Błąd podczas importu ustawień. Sprawdź format pliku.');
            }
        };
        reader.readAsText(file);
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Ustawienia panelu</h1>
                <p className={styles.subtitle}>Konfiguracja panelu administracyjnego</p>
            </div>

            <div className={styles.settingsGrid}>
                {/* Wygląd i Motyw */}
                <div className={styles.settingsCard}>
                    <h2 className={styles.cardTitle}>🎨 Wygląd i Interfejs</h2>

                    <div className={styles.settingItem}>
                        <label className={styles.settingLabel}>Motyw interfejsu</label>
                        <div className={styles.themeToggle}>
                            <button
                                className={`${styles.themeButton} ${!isDarkMode ? styles.active : ''}`}
                                onClick={() => handleThemeChange(false)}
                            >
                                ☀️ Jasny
                            </button>
                            <button
                                className={`${styles.themeButton} ${isDarkMode ? styles.active : ''}`}
                                onClick={() => handleThemeChange(true)}
                            >
                                🌙 Ciemny
                            </button>
                        </div>
                        <p className={styles.settingDescription}>
                            Wybierz preferowany motyw kolorystyczny panelu
                        </p>
                    </div>

                    <div className={styles.settingItem}>
                        <div className={styles.checkboxContainer}>
                            <input
                                id="compactMode"
                                type="checkbox"
                                checked={compactMode}
                                onChange={(e) => setCompactMode(e.target.checked)}
                                className={styles.checkbox}
                            />
                            <label htmlFor="compactMode" className={styles.checkboxLabel}>
                                Tryb kompaktowy
                            </label>
                        </div>
                        <p className={styles.settingDescription}>
                            Zmniejsz odstępy między elementami dla większej gęstości informacji
                        </p>
                    </div>
                </div>

                {/* Ustawienia Ogólne */}
                <div className={styles.settingsCard}>
                    <h2 className={styles.cardTitle}>⚙️ Ustawienia Ogólne</h2>

                    <div className={styles.settingItem}>
                        <label className={styles.settingLabel} htmlFor="siteName">
                            Nazwa platformy
                        </label>
                        <input
                            id="siteName"
                            type="text"
                            value={siteName}
                            onChange={(e) => setSiteName(e.target.value)}
                            className={styles.textInput}
                            placeholder="Wprowadź nazwę platformy"
                        />
                        <p className={styles.settingDescription}>
                            Nazwa wyświetlana w nagłówku i tytule strony
                        </p>
                    </div>

                    <div className={styles.settingItem}>
                        <label className={styles.settingLabel} htmlFor="language">
                            Język interfejsu
                        </label>
                        <select
                            id="language"
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className={styles.selectInput}
                        >
                            <option value="pl">Polski</option>
                            <option value="en">English</option>
                            <option value="de">Deutsch</option>
                            <option value="fr">Français</option>
                            <option value="es">Español</option>
                            <option value="it">Italiano</option>
                        </select>
                        <p className={styles.settingDescription}>
                            Domyślny język interfejsu użytkownika
                        </p>
                    </div>

                    <div className={styles.settingItem}>
                        <label className={styles.settingLabel} htmlFor="itemsPerPage">
                            Elementy na stronę
                        </label>
                        <select
                            id="itemsPerPage"
                            value={itemsPerPage}
                            onChange={(e) => setItemsPerPage(parseInt(e.target.value))}
                            className={styles.selectInput}
                        >
                            <option value={10}>10</option>
                            <option value={20}>20</option>
                            <option value={50}>50</option>
                            <option value={100}>100</option>
                        </select>
                        <p className={styles.settingDescription}>
                            Domyślna liczba elementów wyświetlanych na jednej stronie w tabelach
                        </p>
                    </div>
                </div>

                {/* Funkcjonalność */}
                <div className={styles.settingsCard}>
                    <h2 className={styles.cardTitle}>🚀 Funkcjonalność</h2>

                    <div className={styles.settingItem}>
                        <div className={styles.checkboxContainer}>
                            <input
                                id="autoSave"
                                type="checkbox"
                                checked={autoSave}
                                onChange={(e) => setAutoSave(e.target.checked)}
                                className={styles.checkbox}
                            />
                            <label htmlFor="autoSave" className={styles.checkboxLabel}>
                                Automatyczne zapisywanie
                            </label>
                        </div>
                        <p className={styles.settingDescription}>
                            Automatycznie zapisuj zmiany w formularzach co 30 sekund
                        </p>
                    </div>

                    <div className={styles.settingItem}>
                        <div className={styles.checkboxContainer}>
                            <input
                                id="showTutorials"
                                type="checkbox"
                                checked={showTutorials}
                                onChange={(e) => setShowTutorials(e.target.checked)}
                                className={styles.checkbox}
                            />
                            <label htmlFor="showTutorials" className={styles.checkboxLabel}>
                                Pokaż samouczki
                            </label>
                        </div>
                        <p className={styles.settingDescription}>
                            Wyświetlaj wskazówki i samouczki dla nowych funkcji
                        </p>
                    </div>
                </div>

                {/* Import/Export */}
                <div className={styles.settingsCard}>
                    <h2 className={styles.cardTitle}>💾 Zarządzanie Ustawieniami</h2>

                    <div className={styles.settingItem}>
                        <label className={styles.settingLabel}>Eksport ustawień</label>
                        <button onClick={handleExportSettings} className={styles.exportButton}>
                            📤 Eksportuj ustawienia
                        </button>
                        <p className={styles.settingDescription}>
                            Pobierz plik z aktualnymi ustawieniami panelu
                        </p>
                    </div>

                    <div className={styles.settingItem}>
                        <label className={styles.settingLabel} htmlFor="importFile">
                            Import ustawień
                        </label>
                        <input
                            id="importFile"
                            type="file"
                            accept=".json"
                            onChange={handleImportSettings}
                            className={styles.fileInput}
                        />
                        <p className={styles.settingDescription}>
                            Wczytaj ustawienia z wcześniej wyeksportowanego pliku
                        </p>
                    </div>

                    <div className={styles.settingItem}>
                        <label className={styles.settingLabel}>Informacje o systemie</label>
                        <div className={styles.systemInfo}>
                            <div className={styles.infoRow}>
                                <span>Wersja panelu:</span>
                                <strong>v1.0.0</strong>
                            </div>
                            <div className={styles.infoRow}>
                                <span>Ostatnia aktualizacja:</span>
                                <strong>{new Date().toLocaleDateString('pl-PL')}</strong>
                            </div>
                            <div className={styles.infoRow}>
                                <span>Użytkownik:</span>
                                <strong>Administrator</strong>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Przyciski akcji */}
            <div className={styles.actions}>
                <button onClick={handleSave} className={styles.saveButton}>
                    💾 Zapisz ustawienia
                </button>
                <button onClick={handleReset} className={styles.resetButton}>
                    🔄 Przywróć domyślne
                </button>
            </div>
        </div>
    );
};

export default SettingsPage;

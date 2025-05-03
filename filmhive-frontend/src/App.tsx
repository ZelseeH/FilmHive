import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './layouts/Navbar/Navbar';
import Footer from './layouts/Footer/Footer';
import AppRoutes from './routes';
import GeminiChatbot from './components/GeminiChatbot/GeminiChatbot';
import styles from './App.module.css';
import "primereact/resources/themes/lara-light-indigo/theme.css";
import "primereact/resources/primereact.min.css";
import "primeicons/primeicons.css";
import "./styles/primereact-custom.css";

const App: React.FC = () => {
  return (
    <AuthProvider>
      <div className={styles.app}>
        <Navbar />
        <div className={styles.content}>
          <AppRoutes />
        </div>
        <Footer />
        <GeminiChatbot />  {/* Dodaj ten komponent tutaj */}
      </div>
    </AuthProvider>
  );
}

export default App;

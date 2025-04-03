// App.tsx
import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar/Navbar';
import Footer from './components/Footer/Footer';
import AppRoutes from './routes';
import styles from './App.module.css';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <div className={styles.app}>
        <Navbar />
        <div className={styles.content}>
          <AppRoutes />
        </div>
        <Footer />
      </div>
    </AuthProvider>
  );
}

export default App;

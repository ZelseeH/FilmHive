import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar/Navbar';
import Footer from './components/Footer/Footer'; // Dodaj import Footer
import HomePage from './pages/HomePage';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Navbar />
        <div className="content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            {/* Tutaj będą dodatkowe ścieżki */}
          </Routes>
        </div>
        <Footer /> {/* Dodaj komponent Footer */}
      </div>
    </AuthProvider>
  );
}

export default App;

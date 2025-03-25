import React from 'react';
import Navbar from './components/Navbar/Navbar.jsx';
import MainContent from './components/MainContent/MainContent.jsx';
import Footer from './components/Footer/Footer.jsx'; // Importujemy Footer
import "./App.css";
function App() {
  return (
    <div className="App">
      <Navbar />
      <MainContent />
      <Footer /> 
    </div>
  );
}

export default App;

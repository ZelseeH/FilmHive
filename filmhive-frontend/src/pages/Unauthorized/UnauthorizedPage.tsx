import React from 'react';
import { Link } from 'react-router-dom';

const UnauthorizedPage: React.FC = () => {
    return (
        <div className="unauthorized-page">
            <h1>Brak dostępu</h1>
            <p>Nie masz uprawnień do wyświetlenia tej strony.</p>
            <Link to="/" className="btn">Wróć na stronę główną</Link>
        </div>
    );
};

export default UnauthorizedPage;

export const renderLoadingState = (className: string, message = 'Ładowanie...') => (
    <div className={className} > {message} </div>
);

export const renderErrorState = (className: string, error: string) => (
    <div className={className} > Błąd: {error}</div>
);

export const renderEmptyState = (className: string, message = 'Nie znaleziono danych') => (
    <div className={className} > {message} </div>
);

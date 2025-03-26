// src/utils/api.js
export const fetchWithAuth = async (url, options = {}) => {
    const token = localStorage.getItem('token');
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });
    
    if (response.status === 401) {
      // Token wygasł lub jest nieważny
      localStorage.removeItem('token');
      window.location.reload();
      throw new Error('Sesja wygasła. Zaloguj się ponownie.');
    }
    
    return response;
  };
  
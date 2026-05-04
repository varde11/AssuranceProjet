import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getMe } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken]   = useState(() => localStorage.getItem('varde_token') || null);
  const [user,  setUser]    = useState(null);
  const [loading, setLoading] = useState(!!localStorage.getItem('varde_token'));

  const fetchUser = useCallback(async (tk) => {
    try {
      const me = await getMe(tk);
      setUser(me);
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  }, []); // eslint-disable-line

  useEffect(() => {
    if (token) fetchUser(token);
  }, [token, fetchUser]);

  function loginSuccess(access_token) {
    localStorage.setItem('varde_token', access_token);
    setToken(access_token);
  }

  function logout() {
    localStorage.removeItem('varde_token');
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ token, user, loading, loginSuccess, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

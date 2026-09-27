import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const login = (username, password) => {
    // For demo purposes, we accept any login and assign roles based on username
    let role = 'investigator'; // Default
    if (username.toLowerCase() === 'admin') {
      role = 'admin';
    } else if (username.toLowerCase() === 'viewer') {
      role = 'viewer';
    }
    setUser({ username, role });
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

import { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access");

    if (!token) {
      setLoading(false);
      return;
    }

    api.get("/users/me/")
      .then((response) => setUser(response.data))
      .catch(() => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const response = await api.post("/auth/login/", {
      email,
      password,
    });

    localStorage.setItem("access", response.data.access);
    localStorage.setItem("refresh", response.data.refresh);

    let profileData = response.data.user;
    try {
      const profile = await api.get("/users/me/");
      profileData = profile.data;
    } catch {
      // Use user object returned from login response
    }
    setUser(profileData);

    return profileData;
  };

  const register = async (data) => {
    const response = await api.post("/auth/register/", data);

    localStorage.setItem("access", response.data.access);
    localStorage.setItem("refresh", response.data.refresh);

    let profileData = response.data.user;
    try {
      const profile = await api.get("/users/me/");
      profileData = profile.data;
    } catch {
      // Use user object returned from register response
    }
    setUser(profileData);

    return profileData;
  };

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, setUser, loading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

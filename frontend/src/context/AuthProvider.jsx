import { useCallback, useEffect, useMemo, useState } from "react";
import api, { TOKEN_KEY } from "../api/client";
import { AuthContext } from "./auth-context";

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() =>
    Boolean(localStorage.getItem(TOKEN_KEY))
  );

  // On page load, if a token exists, fetch the user it belongs to
  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) return;
    api
      .get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    const me = await api.get("/auth/me");
    setUser(me.data);
  }, []);

  const register = useCallback(
    async (name, email, password) => {
      await api.post("/auth/register", { name, email, password });
      await login(email, password);
    },
    [login]
  );

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
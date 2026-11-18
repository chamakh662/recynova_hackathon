import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../../context/AuthContext";

function LoginForm() {
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      window.location.href = "/dashboard";
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.error ||
        "Email ou mot de passe incorrect."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      {error && <p className="error-message">{error}</p>}

      <div className="form-group">
        <label htmlFor="login-email">Adresse email</label>
        <input
          id="login-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="exemple@email.com"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="login-password">Mot de passe</label>
        <input
          id="login-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "Connexion..." : "Se connecter"}
      </button>

      <p>
        Vous n'avez pas de compte ? <Link to="/register">S'inscrire</Link>
      </p>
    </form>
  );
}

export default LoginForm;

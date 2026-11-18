import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../context/AuthContext";

function RegisterForm() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [nom, setNom] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Les mots de passe ne correspondent pas.");
      return;
    }

    setLoading(true);

    try {
      await register({ nom, email, password });
      navigate("/dashboard");
    } catch (err) {
      const data = err.response?.data;
      setError(
        data?.error ||
        data?.detail ||
        data?.message ||
        data?.email?.[0] ||
        data?.password?.[0] ||
        (err.message === "Network Error"
          ? "Impossible de joindre le serveur. Vérifiez que le backend est démarré."
          : "Impossible de créer le compte.")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      {error && <p className="error-message">{error}</p>}

      <div className="form-group">
        <label htmlFor="register-nom">Nom complet</label>
        <input
          id="register-nom"
          value={nom}
          onChange={(e) => setNom(e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="register-email">Email</label>
        <input
          id="register-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="register-password">Mot de passe</label>
        <input
          id="register-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          minLength="8"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="register-confirm">Confirmer le mot de passe</label>
        <input
          id="register-confirm"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "Création du compte..." : "Créer mon compte"}
      </button>

      <p>
        Vous avez déjà un compte ? <Link to="/login">Se connecter</Link>
      </p>
    </form>
  );
}

export default RegisterForm;
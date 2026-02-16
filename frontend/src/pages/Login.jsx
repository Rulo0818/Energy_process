import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Login.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Por ahora, simular login basado en los usuarios de init_db.py
      if (email === "admin@example.com" && password === "admin123") {
        const userData = {
          id: 1,
          email: "admin@example.com",
          nombre: "Administrador",
          rol: "admin"
        };
        login(userData);
        navigate("/");
      } else if (email === "operador1@example.com" && password === "operador123") {
        const userData = {
          id: 2,
          email: "operador1@example.com",
          nombre: "Operador Uno",
          rol: "operador"
        };
        login(userData);
        navigate("/");
      } else if (email === "user@example.com" && password === "user123") {
        // Mantener este para compatibilidad si el usuario lo usaba
        const userData = {
          id: 1, // Mapear a admin por ahora
          email: "user@example.com",
          nombre: "Usuario Test",
          rol: "admin"
        };
        login(userData);
        navigate("/");
      } else {
        setError("Credenciales inválidas");
      }
    } catch (err) {
      setError("Error al iniciar sesión");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>⚡ Energy Process</h1>
          <p>Sistema de Procesamiento de Energía Excedentaria</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@email.com"
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={loading}
              required
            />
          </div>

          {error && <div className="form-error">{error}</div>}

          <button type="submit" disabled={loading} className="btn-login">
            {loading ? "Iniciando..." : "Iniciar sesión"}
          </button>
        </form>

        <div className="login-footer">
          <p className="text-muted">Credenciales de prueba:</p>
          <small>
            <strong>Admin:</strong> admin@example.com / admin123<br/>
            <strong>Usuario:</strong> user@example.com / user123
          </small>
        </div>
      </div>
    </div>
  );
}

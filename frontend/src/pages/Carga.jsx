import { useState } from "react";
import { uploadArchivo } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Carga() {
  const { user } = useAuth();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage({ type: "error", text: "Selecciona un archivo" });
      return;
    }
    setLoading(true);
    setMessage({ type: "", text: "" });
    try {
      // Usar el ID del usuario logueado o fallback a 1
      const usuarioId = user?.id || 1;
      const { data } = await uploadArchivo(file, usuarioId);
      setMessage({
        type: "success",
        text: `Archivo en cola (ID: ${data.archivo_id}). Estado: ${data.estado}. Puedes ver el estado en Archivos.`,
      });
      setFile(null);
      e.target.reset();
    } catch (err) {
      const detail = err.response?.data?.detail || err.message;
      setMessage({ type: "error", text: String(detail) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Subir archivo de peajes</h1>
        <p className="page-subtitle">sube un archivo de peajes para procesarlo</p>
      </header>

      <div className="card">
        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label className="form-label">Archivo (CSV / TXT / XML )</label>
            <input
              type="file"
              accept=".csv,.txt,.xml"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="form-input form-input--file"
            />
          </div>
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? "Subiendo…" : "Subir archivo"}
          </button>
        </form>
        {message.text && (
          <p
            className={
              message.type === "error"
                ? "form-message form-message--error"
                : "form-message form-message--success"
            }
          >
            {message.text}
          </p>
        )}
      </div>
    </div>
  );
}

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getArchivos, getArchivoStatus, getErroresArchivo, getEnergia } from "../services/api";

const formatDate = (dateStr) => {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const estadoColor = (estado) => {
  switch (estado) {
    case "completado":
      return "var(--success)";
    case "error":
    case "pendiente":
      return "var(--warning)";
    case "procesando":
      return "var(--accent)";
    default:
      return "var(--text-secondary)";
  }
};

export default function Archivos() {
  const { id } = useParams();
  const [archivos, setArchivos] = useState([]);
  const [detalle, setDetalle] = useState(null);
  const [errores, setErrores] = useState([]);
  const [registrosOk, setRegistrosOk] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingDetalle, setLoadingDetalle] = useState(false);

  const loadArchivos = () => {
    setLoading(true);
    getArchivos(50)
      .then((res) => setArchivos(res.data || []))
      .catch(() => setArchivos([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadArchivos();
  }, []);

  const loadDetalle = () => {
    if (!id) return;
    setLoadingDetalle(true);
    Promise.all([
      getArchivoStatus(id),
      getErroresArchivo(id),
      getEnergia({ archivo_id: parseInt(id, 10) }),
    ])
      .then(([aRes, eRes, enRes]) => {
        setDetalle(aRes.data);
        setErrores(Array.isArray(eRes.data) ? eRes.data : []);
        setRegistrosOk(enRes.data?.registros ?? []);
      })
      .catch(() => {
        setDetalle(null);
        setErrores([]);
        setRegistrosOk([]);
      })
      .finally(() => setLoadingDetalle(false));
  };

  useEffect(() => {
    if (!id) {
      setDetalle(null);
      setErrores([]);
      setRegistrosOk([]);
      return;
    }
    loadDetalle();
  }, [id]);

  if (id) {
    return (
      <div className="page">
        <header className="page-header">
          <Link to="/archivos" className="back-link">← Volver a archivos</Link>
          <h1 className="page-title">
            {loadingDetalle ? "Cargando…" : detalle?.nombre_archivo || `Archivo #${id}`}
          </h1>
          {detalle && (
            <p className="page-subtitle">
              Estado: <span style={{ color: estadoColor(detalle.estado) }}>{detalle.estado}</span>
              {" · "}
              {detalle.registros_exitosos ?? 0} registros · {detalle.registros_con_error ?? 0} errores
              {" · "}
              {formatDate(detalle.fecha_carga)}
            </p>
          )}
        </header>

        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
            <h2 className="card-title">Registros OK ({registrosOk.length})</h2>
            <button type="button" className="btn btn-sm" onClick={loadDetalle} disabled={loadingDetalle}>
              {loadingDetalle ? "Cargando…" : "Refrescar"}
            </button>
          </div>
          {loadingDetalle ? (
            <p className="text-muted">Cargando…</p>
          ) : registrosOk.length === 0 ? (
            <p className="empty-state">No hay registros correctos para este archivo.</p>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>CUPS</th>
                    <th>Desde</th>
                    <th>kWh Gen</th>
                    <th>kWh Cons</th>
                    <th>Pago (€)</th>
                  </tr>
                </thead>
                <tbody>
                  {registrosOk.map((r) => (
                    <tr key={r.id}>
                      <td>{r.cups_cliente || "—"}</td>
                      <td>{r.fecha_desde ? new Date(r.fecha_desde).toLocaleDateString() : "—"}</td>
                      <td>{r.total_neta_gen != null ? Number(r.total_neta_gen).toFixed(2) : "—"}</td>
                      <td>{r.total_autoconsumida != null ? Number(r.total_autoconsumida).toFixed(2) : "—"}</td>
                      <td>{r.total_pago != null ? Number(r.total_pago).toFixed(2) : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
            <h2 className="card-title">Errores en este archivo ({errores.length})</h2>
            <button type="button" className="btn btn-sm" onClick={loadDetalle} disabled={loadingDetalle}>
              {loadingDetalle ? "Cargando…" : "Refrescar errores"}
            </button>
          </div>
          {detalle?.estado === "procesando" && (
            <p className="text-muted" style={{ marginBottom: "0.5rem" }}>
              El archivo se está procesando. Refresca en unos segundos para ver los errores.
            </p>
          )}
          {loadingDetalle ? (
            <p className="text-muted">Cargando…</p>
          ) : errores.length === 0 ? (
            <p className="empty-state">
              {detalle?.estado === "completado" ? "Sin errores para este archivo." : "Aún no hay errores cargados. Si el archivo está procesando, usa «Refrescar errores»."}
            </p>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Línea</th>
                    <th>Tipo</th>
                    <th>Descripción</th>
                  </tr>
                </thead>
                <tbody>
                  {errores.map((e) => (
                    <tr key={e.id}>
                      <td>{e.linea_archivo}</td>
                      <td>
                        <span className="table-badge" style={{ background: "var(--warning)" }}>
                          {e.tipo_error}
                        </span>
                      </td>
                      <td>{e.descripcion}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Archivos y errores</h1>
        <p className="page-subtitle">
          Listado de archivos procesados. Haz clic en uno para ver sus errores.
        </p>
      </header>

      <div className="card">
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "0.75rem" }}>
          <button type="button" className="btn btn-sm" onClick={loadArchivos} disabled={loading}>
            {loading ? "Cargando…" : "Refrescar lista"}
          </button>
        </div>
        {loading ? (
          <p className="text-muted">Cargando…</p>
        ) : archivos.length === 0 ? (
          <p className="empty-state">
            Aún no hay archivos. <Link to="/carga">Sube uno</Link>.
          </p>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Estado</th>
                  <th>Registros OK</th>
                  <th>Errores</th>
                  <th>Fecha</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {archivos.map((a) => (
                  <tr key={a.id}>
                    <td>{a.nombre_archivo}</td>
                    <td>
                      <span
                        className="table-badge"
                        style={{ background: estadoColor(a.estado) }}
                      >
                        {a.estado}
                      </span>
                    </td>
                    <td>{a.registros_exitosos ?? 0}</td>
                    <td>{a.registros_con_error ?? 0}</td>
                    <td className="text-muted">{formatDate(a.fecha_carga)}</td>
                    <td style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                      <Link to={`/archivos/${a.id}`} className="btn btn-sm">
                        Ver registros OK
                      </Link>
                      <Link to={`/archivos/${a.id}`} className="btn btn-sm" style={{ background: "var(--warning)", color: "#1a1a1a" }}>
                        Ver errores
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

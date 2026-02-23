import { useState, useEffect } from "react";
import { getArchivos, getEnergia, api } from "../services/api";
import "./DataViewer.css";

export default function DataViewer() {
  const [archivos, setArchivos] = useState([]);
  const [energia, setEnergia] = useState([]);
  const [errores, setErrores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("archivos");

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [archivosRes, energiaRes, erroresRes] = await Promise.all([
          getArchivos(100),
          getEnergia(),
          api.get("/api/v1/errores").catch(() => ({ data: [] }))
        ]);

        setArchivos(archivosRes.data || []);
        setEnergia(energiaRes.data?.registros || []);
        setErrores(Array.isArray(erroresRes.data) ? erroresRes.data : []);
      } catch (error) {
        console.error("Error cargando datos:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 5000); // Actualizar cada 5 segundos
    return () => clearInterval(interval);
  }, []);

  if (loading && archivos.length === 0 && energia.length === 0) {
    return <div className="data-viewer-loading">Cargando datos...</div>;
  }

  return (
    <div className="data-viewer">
      <div className="tabs">
        <button
          className={`tab ${activeTab === "archivos" ? "active" : ""}`}
          onClick={() => setActiveTab("archivos")}
        >
          Archivos ({archivos.length})
        </button>
        <button
          className={`tab ${activeTab === "energia" ? "active" : ""}`}
          onClick={() => setActiveTab("energia")}
        >
           Energía ({energia.length})
        </button>
        <button
          className={`tab ${activeTab === "errores" ? "active" : ""}`}
          onClick={() => setActiveTab("errores")}
        >
          Errores ({errores.length})
        </button>
      </div>

      <div className="tab-content">
        {activeTab === "archivos" && (
          <div className="table-container">
            {archivos.length > 0 ? (
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Estado</th>
                    <th>Total</th>
                    <th>OK</th>
                    <th>Errores</th>
                    <th>Creado</th>
                  </tr>
                </thead>
                <tbody>
                  {archivos.map((archivo) => (
                    <tr key={archivo.id}>
                      <td>#{archivo.id}</td>
                      <td>{archivo.nombre_archivo}</td>
                      <td>
                        <span className={`badge badge-${archivo.estado}`}>
                          {archivo.estado}
                        </span>
                      </td>
                      <td>{archivo.total_registros || 0}</td>
                      <td style={{ color: "#4caf50" }}>{archivo.registros_exitosos || 0}</td>
                      <td style={{ color: "#f44336" }}>{archivo.registros_con_error || 0}</td>
                      <td>{new Date(archivo.fecha_carga).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-message">No hay archivos en la base de datos</p>
            )}
          </div>
        )}

        {activeTab === "energia" && (
          <div className="table-container">
            {energia.length > 0 ? (
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>CUPS</th>
                    <th>Desde</th>
                    <th>kWh Gen</th>
                    <th>kWh Cons</th>
                    <th>Pago (€)</th>
                  </tr>
                </thead>
                <tbody>
                  {energia.map((reg) => (
                    <tr key={reg.id}>
                      <td>#{reg.id}</td>
                      <td>{reg.cups_cliente || "—"}</td>
                      <td>{reg.fecha_desde ? new Date(reg.fecha_desde).toLocaleDateString() : "—"}</td>
                      <td style={{ fontWeight: 'bold' }}>{reg.total_neta_gen?.toFixed(2) || "0.00"}</td>
                      <td>{reg.total_autoconsumida?.toFixed(2) || "0.00"}</td>
                      <td style={{ color: '#2c3e50', fontWeight: 'bold' }}>{reg.total_pago?.toFixed(2) || "0.00"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-message">No hay registros de energía en la base de datos</p>
            )}
          </div>
        )}

        {activeTab === "errores" && (
          <div className="table-container">
            {errores.length > 0 ? (
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Archivo</th>
                    <th>Línea</th>
                    <th>Descripción</th>
                    <th>Tipo</th>
                  </tr>
                </thead>
                <tbody>
                  {errores.map((error) => (
                    <tr key={error.id}>
                      <td>#{error.id}</td>
                      <td>Archivo #{error.archivo_id}</td>
                      <td>{error.linea_archivo}</td>
                      <td>{error.descripcion}</td>
                      <td>
                        <span className="badge badge-error">{error.tipo_error}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-message">No hay errores registrados</p>
            )}
          </div>
        )}
      </div>

      <div className="data-viewer-footer">
        <small>Última actualización: {new Date().toLocaleTimeString()}</small>
      </div>
    </div>
  );
}

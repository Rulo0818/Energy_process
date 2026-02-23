import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const API_TIMEOUT_MS = 12_000;

export const api = axios.create({
  baseURL,
  timeout: API_TIMEOUT_MS,
  headers: { "Content-Type": "application/json" },
});

export const uploadArchivo = (file, usuarioId = 1) => {
  const form = new FormData();
  form.append("file", file);
  form.append("usuario_id", usuarioId);
  return api.post("/api/v1/archivos/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getArchivoStatus = (archivoId) =>
  api.get(`/api/v1/archivos/${archivoId}`);

export const getEnergia = (params = {}) =>
  api.get("/api/v1/energia", { params });

export const getErroresArchivo = (archivoId) =>
  api.get(`/api/v1/errores/${archivoId}`);

export const getArchivos = (limit = 20) =>
  api.get("/api/v1/archivos", { params: { limit } });

export const getStats = () => api.get("/api/v1/stats");

// Usuarios
export const getUsuarios = (params = {}) =>
  api.get("/api/v1/usuarios", { params });

export const getUsuario = (id) =>
  api.get(`/api/v1/usuarios/${id}`);

export const createUsuario = (data) =>
  api.post("/api/v1/usuarios", data);

export const updateUsuario = (id, data) =>
  api.put(`/api/v1/usuarios/${id}`, data);

export const deleteUsuario = (id) =>
  api.delete(`/api/v1/usuarios/${id}`);

export const getUsuariosStats = () =>
  api.get("/api/v1/usuarios/stats/resumen");

// Clientes
export const getClientes = (params = {}) =>
  api.get("/api/v1/clientes", { params });

export const getCliente = (id) =>
  api.get(`/api/v1/clientes/${id}`);

export const getClienteByCups = (cups) =>
  api.get(`/api/v1/clientes/cups/${cups}`);

export const createCliente = (data) =>
  api.post("/api/v1/clientes", data);

export const updateCliente = (id, data) =>
  api.put(`/api/v1/clientes/${id}`, data);

export const deleteCliente = (id) =>
  api.delete(`/api/v1/clientes/${id}`);

export const getClientesStats = () =>
  api.get("/api/v1/clientes/stats/resumen");

export const getClienteWithEnergia = (id) =>
  api.get(`/api/v1/clientes/${id}/energia`);

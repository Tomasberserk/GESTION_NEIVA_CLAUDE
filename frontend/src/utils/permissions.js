/**
 * Utilidades de permisos y verificación de roles para Gestión Neiva.
 * NOTA: El frontend es exclusivamente capa de experiencia de usuario (UX).
 * La seguridad y autorización real la impone estrictamente el backend FastAPI.
 */

export function isAdmin(usuario) {
  return usuario?.rol === 'admin'
}

export function isTendero(usuario) {
  return usuario?.rol === 'tendero'
}

export function canViewAdminModules(usuario) {
  return isAdmin(usuario)
}

export function canManageEmployees(usuario) {
  return isAdmin(usuario)
}

export function canEditProducts(usuario) {
  return isAdmin(usuario)
}

export function canExportReports(usuario) {
  return isAdmin(usuario)
}

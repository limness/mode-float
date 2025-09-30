const KEYCLOAK_LOGIN_URL = import.meta.env.VITE_KEYCLOAK_LOGIN_URL

if (!KEYCLOAK_LOGIN_URL) {
  console.warn('[auth] VITE_KEYCLOAK_LOGIN_URL is not defined. Login redirect will fallback to root.')
}

export function redirectToKeycloakLogin() {
  const target = KEYCLOAK_LOGIN_URL ?? '/'
  window.location.href = target
}

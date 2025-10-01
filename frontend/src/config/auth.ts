const RAW_KEYCLOAK_LOGIN_URL = import.meta.env.VITE_KEYCLOAK_LOGIN_URL?.trim()

function resolveKeycloakLoginUrl(): string | null {
  if (!RAW_KEYCLOAK_LOGIN_URL) {
    console.warn('[auth] VITE_KEYCLOAK_LOGIN_URL is not defined. Keycloak redirect is disabled.')
    return null
  }

  if (!/^https?:\/\//i.test(RAW_KEYCLOAK_LOGIN_URL)) {
    console.error('[auth] VITE_KEYCLOAK_LOGIN_URL must be an absolute URL (http/https).')
    return null
  }

  try {
    if (typeof window !== 'undefined') {
      const parsed = new URL(RAW_KEYCLOAK_LOGIN_URL)
      if (
        parsed.origin === window.location.origin &&
        parsed.pathname.replace(/\/?$/, '') === window.location.pathname.replace(/\/?$/, '')
      ) {
        console.error('[auth] VITE_KEYCLOAK_LOGIN_URL points to the current page and would cause a redirect loop.')
        return null
      }
    }
  } catch (error) {
    console.error('[auth] Failed to parse VITE_KEYCLOAK_LOGIN_URL:', error)
    return null
  }

  return RAW_KEYCLOAK_LOGIN_URL
}

const KEYCLOAK_LOGIN_URL = resolveKeycloakLoginUrl()

export function getKeycloakLoginUrl() {
  return KEYCLOAK_LOGIN_URL
}

export function redirectToKeycloakLogin() {
  if (!KEYCLOAK_LOGIN_URL) {
    return
  }
  window.location.href = KEYCLOAK_LOGIN_URL
}

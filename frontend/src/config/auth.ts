const KEYCLOAK_LOGIN_URL = import.meta.env.VITE_KEYCLOAK_LOGIN_URL?.trim()

function isValidUrl(url: string): boolean {
  try {
    // new URL throws if URL is malformed
    void new URL(url)
    return true
  } catch (error) {
    console.error('[auth] Invalid VITE_KEYCLOAK_LOGIN_URL:', error)
    return false
  }
}

function isLoopback(url: string): boolean {
  if (typeof window === 'undefined') {
    return false
  }

  try {
    const target = new URL(url)
    const current = window.location
    return (
      target.origin === current.origin &&
      target.pathname.replace(/\/$/, '') === current.pathname.replace(/\/$/, '')
    )
  } catch (error) {
    console.error('[auth] Failed to inspect VITE_KEYCLOAK_LOGIN_URL:', error)
    return false
  }
}

export function redirectToKeycloakLogin() {
  if (!KEYCLOAK_LOGIN_URL) {
    console.error('[auth] VITE_KEYCLOAK_LOGIN_URL is not set. Keycloak redirect cancelled.')
    return
  }

  if (!isValidUrl(KEYCLOAK_LOGIN_URL)) {
    return
  }

  if (isLoopback(KEYCLOAK_LOGIN_URL)) {
    console.error('[auth] VITE_KEYCLOAK_LOGIN_URL points to the current page. Redirect aborted to avoid loop.')
    return
  }

  window.location.href = KEYCLOAK_LOGIN_URL
}

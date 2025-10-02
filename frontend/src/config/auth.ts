const RAW_KEYCLOAK_LOGIN_URL = import.meta.env.VITE_KEYCLOAK_LOGIN_URL?.trim()
const FALLBACK_KEYCLOAK_LOGIN_URL = '/oauth2/start'

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

interface KeycloakLoginInfo {
  url: string | null
  error: string | null
}

const resolvedLoginInfo: KeycloakLoginInfo = (() => {
  if (!RAW_KEYCLOAK_LOGIN_URL) {
    return { url: FALLBACK_KEYCLOAK_LOGIN_URL, error: null }
  }

  if (!isValidUrl(RAW_KEYCLOAK_LOGIN_URL)) {
    return {
      url: FALLBACK_KEYCLOAK_LOGIN_URL,
      error: 'Некорректный URL Keycloak. Используем резервный вход через /oauth2/start.',
    }
  }

  if (isLoopback(RAW_KEYCLOAK_LOGIN_URL)) {
    return {
      url: FALLBACK_KEYCLOAK_LOGIN_URL,
      error: 'URL авторизации указывает на текущую страницу. Используем резервный вход через /oauth2/start.',
    }
  }

  return { url: RAW_KEYCLOAK_LOGIN_URL, error: null }
})()

export function getKeycloakLoginInfo(): KeycloakLoginInfo {
  return resolvedLoginInfo
}

export function redirectToKeycloakLogin() {
  const { url } = resolvedLoginInfo
  if (!url) {
    console.error('[auth] Keycloak login URL is invalid or missing. Redirect cancelled.')
    return
  }
  window.location.href = url
}

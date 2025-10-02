import { useEffect } from 'react'
import { getKeycloakLoginInfo, redirectToKeycloakLogin } from '../config/auth'

export function LoginPage() {
  const { url: keycloakUrl, error: configError } = getKeycloakLoginInfo()
  const isFallback = keycloakUrl === '/oauth2/start'

  useEffect(() => {
    if (isFallback && keycloakUrl) {
      redirectToKeycloakLogin()
    }
  }, [isFallback, keycloakUrl])

  const handleLogin = () => {
    if (!keycloakUrl) {
      return
    }
    redirectToKeycloakLogin()
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">
          Войти в <span className="auth-title__accent">Fly Potato</span>
        </h1>
        <p className="auth-card__subtitle">Авторизация проходит через корпоративный Keycloak.</p>

        {!isFallback && (
          <div className="auth-form auth-form--actions">
            <button className="auth-submit" type="button" onClick={handleLogin} disabled={!keycloakUrl}>
              Продолжить
            </button>
          </div>
        )}
        {isFallback && (
          <p className="auth-card__hint">Перенаправляем через /oauth2/start…</p>
        )}
        {configError && <p className="auth-card__error" role="alert">{configError}</p>}
        <p className="auth-card__footer">Используйте корпоративный аккаунт или провайдеры, подключённые в Keycloak (например, Google).</p>
      </div>
    </div>
  )
}
